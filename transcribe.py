"""Motore di trascrizione: mlx-whisper (accelerazione Metal su Apple Silicon).

Il valore "nostro" qui e' l'iniezione del glossario via initial_prompt, non il modello.
"""
import mlx_whisper

import audio

# nome breve in config.yaml -> repo HuggingFace (scaricato una volta da download_models.py)
REPOS = {
    "small": "mlx-community/whisper-small-mlx",
    "medium": "mlx-community/whisper-medium-mlx",
    "large-v3-turbo": "mlx-community/whisper-large-v3-turbo",
    "large-v3-turbo-q4": "mlx-community/whisper-large-v3-turbo-q4",
    "large-v3": "mlx-community/whisper-large-v3-mlx",
}


def repo_for(name):
    if name not in REPOS:
        raise ValueError(f"model.name '{name}' sconosciuto. Ammessi: {', '.join(REPOS)}")
    return REPOS[name]


def _initial_prompt(glossary):
    # initial_prompt di Whisper: ~224 token max. Teniamo i primi termini, gli altri cadono.
    # ponytail: troncamento semplice, se serve rotazione a finestre aggiungila qui.
    terms = [str(t).strip() for t in (glossary or []) if str(t).strip()]
    return ", ".join(terms[:180]) or None


def run(wav_path, cfg, language=None):
    lang = language or cfg.get("language") or "it"
    if lang == "auto":
        lang = None
    result = mlx_whisper.transcribe(
        audio.load_wav(wav_path),  # array 16kHz: mlx-whisper non invoca ffmpeg
        path_or_hf_repo=repo_for(cfg["model"]["name"]),
        language=lang,
        initial_prompt=_initial_prompt(cfg.get("glossary")),
        condition_on_previous_text=False,  # meno "deriva" su lezioni lunghe
    )
    # normalizziamo a lista di dict semplici
    return [
        {"start": float(s["start"]), "end": float(s["end"]), "text": s["text"].strip()}
        for s in result["segments"]
    ]
