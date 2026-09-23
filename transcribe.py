"""Motore di trascrizione.

- Mac Apple Silicon: mlx-whisper (GPU via Metal).
- Windows (e il resto): faster-whisper su CPU, int8.

Il valore "nostro" qui e' l'iniezione del glossario via initial_prompt, non il modello.
"""
import functools
import os
import platform
from pathlib import Path

import audio

APPLE_SILICON = platform.system() == "Darwin" and platform.machine() == "arm64"
# faster-whisper restituisce i segmenti man mano: avanzamento reale. mlx-whisper no.
REPORTS_PROGRESS = not APPLE_SILICON

if os.name == "nt":
    # su Windows i modelli restano dentro la cartella del programma:
    # cancelli la cartella e hai disinstallato tutto.
    os.environ.setdefault("HF_HOME", str(Path(__file__).parent / "models" / "hf"))
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

# nome breve in config.yaml -> modello per ciascun motore
MLX_REPOS = {
    "small": "mlx-community/whisper-small-mlx",
    "medium": "mlx-community/whisper-medium-mlx",
    "large-v3-turbo": "mlx-community/whisper-large-v3-turbo",
    "large-v3-turbo-q4": "mlx-community/whisper-large-v3-turbo-q4",
    "large-v3": "mlx-community/whisper-large-v3-mlx",
}
# faster-whisper non ha il 4 bit: su CPU quantizza a int8 al caricamento, quindi
# "large-v3-turbo-q4" e "large-v3-turbo" sono lo stesso modello.
CT2_MODELS = {
    "small": "small",
    "medium": "medium",
    "large-v3-turbo": "large-v3-turbo",
    "large-v3-turbo-q4": "large-v3-turbo",
    "large-v3": "large-v3",
}


def _check(name):
    if name not in MLX_REPOS:
        raise ValueError(f"model.name '{name}' sconosciuto. Ammessi: {', '.join(MLX_REPOS)}")


def download(name):
    """Scarica il modello (serve internet, una volta). Restituisce la cartella locale."""
    _check(name)
    if APPLE_SILICON:
        from huggingface_hub import snapshot_download
        return snapshot_download(MLX_REPOS[name])
    from faster_whisper import download_model
    return download_model(CT2_MODELS[name])


@functools.lru_cache(maxsize=1)
def _ct2_model(name):
    from faster_whisper import WhisperModel
    # ponytail: solo CPU. Con GPU NVIDIA: device="cuda", compute_type="float16"
    # (servono le librerie CUDA 12 + cuDNN 9 installate a parte).
    try:
        return WhisperModel(CT2_MODELS[name], device="cpu", compute_type="int8",
                            cpu_threads=min(os.cpu_count() or 4, 8), local_files_only=True)
    except Exception as e:
        raise RuntimeError(f"Modello Whisper '{name}' non trovato: riesegui il setup. ({e})") from e


def _initial_prompt(glossary):
    # initial_prompt di Whisper: ~224 token max. Teniamo i primi termini, gli altri cadono.
    # ponytail: troncamento semplice, se serve rotazione a finestre aggiungila qui.
    terms = [str(t).strip() for t in (glossary or []) if str(t).strip()]
    return ", ".join(terms[:180]) or None


def run(wav_path, cfg, language=None, progress=None):
    """progress(frazione 0..1) viene chiamato solo se REPORTS_PROGRESS."""
    name = cfg["model"]["name"]
    _check(name)
    lang = language or cfg.get("language") or "it"
    if lang == "auto":
        lang = None
    samples = audio.load_wav(wav_path)  # array 16kHz: i motori non invocano ffmpeg
    prompt = _initial_prompt(cfg.get("glossary"))

    if APPLE_SILICON:
        import mlx_whisper
        result = mlx_whisper.transcribe(
            samples,
            path_or_hf_repo=MLX_REPOS[name],
            language=lang,
            initial_prompt=prompt,
            condition_on_previous_text=False,  # meno "deriva" su lezioni lunghe
        )
        raw = [(s["start"], s["end"], s["text"]) for s in result["segments"]]
    else:
        # beam_size=1 (greedy) come mlx-whisper: stessa resa del Mac, molto piu' veloce su CPU
        segs, info = _ct2_model(name).transcribe(
            samples,
            language=lang,
            initial_prompt=prompt,
            condition_on_previous_text=False,
            beam_size=1,
        )
        raw = []
        for s in segs:
            raw.append((s.start, s.end, s.text))
            if progress and info.duration:
                progress(min(1.0, s.end / info.duration))

    return [{"start": float(a), "end": float(b), "text": t.strip()} for a, b, t in raw]
