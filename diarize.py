"""Speaker diarization: sherpa-onnx (modelli non gated, nessun account/token).

Modelli scaricati da download_models.py nella cartella models/.
Parametri tarati per contesto tramite i preset "aula" / "riunione" in config.yaml.
"""
import os
from pathlib import Path

import sherpa_onnx

import audio

_M = Path(__file__).parent / "models"
# int8: ~24% piu' veloce della versione fp32 sulla segmentazione (che e' il 95% del costo),
# nessun peggioramento visibile nei test. CoreML/ANE provato: 3x piu' lento, scartato.
SEG_MODEL = str(_M / "sherpa-onnx-pyannote-segmentation-3-0/model.int8.onnx")
EMB_MODEL = str(_M / "wespeaker_en_voxceleb_CAM++.onnx")  # embedding speaker, cross-lingua

# ONNX su piu' core: su un'ora+ di audio single-thread sembra bloccato.
_THREADS = max(2, min(os.cpu_count() or 4, 8))


def run(wav_path, cfg, preset=None, num_speakers=None, progress=None):
    d = cfg["diarization"]
    preset = preset or d.get("preset", "riunione")
    p = d[preset]
    n = num_speakers if num_speakers is not None else p.get("num_speakers")

    config = sherpa_onnx.OfflineSpeakerDiarizationConfig(
        segmentation=sherpa_onnx.OfflineSpeakerSegmentationModelConfig(
            pyannote=sherpa_onnx.OfflineSpeakerSegmentationPyannoteModelConfig(model=SEG_MODEL),
            num_threads=_THREADS,
        ),
        embedding=sherpa_onnx.SpeakerEmbeddingExtractorConfig(model=EMB_MODEL, num_threads=_THREADS),
        clustering=sherpa_onnx.FastClusteringConfig(
            num_clusters=int(n) if n else -1,
            threshold=float(p["cluster_threshold"]),
        ),
        min_duration_on=0.3,
        min_duration_off=0.5,
    )
    sd = sherpa_onnx.OfflineSpeakerDiarization(config)

    cb = None
    if progress:
        def cb(done, total):
            progress(done / total if total else 0.0)
            return 0  # !=0 = abortisci

    segments = sd.process(audio.load_wav(wav_path), callback=cb).sort_by_start_time()
    return [
        {"start": float(s.start), "end": float(s.end), "speaker": f"Speaker {s.speaker + 1}"}
        for s in segments
    ]
