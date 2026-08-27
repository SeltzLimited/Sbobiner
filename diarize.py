"""Speaker diarization: sherpa-onnx (modelli non gated, nessun account/token).

Modelli scaricati da download_models.py nella cartella models/.
Parametri tarati per contesto tramite i preset "aula" / "riunione" in config.yaml.
"""
import wave
import numpy as np
import sherpa_onnx

SEG_MODEL = "models/sherpa-onnx-pyannote-segmentation-3-0/model.onnx"
EMB_MODEL = "models/wespeaker_en_voxceleb_CAM++.onnx"  # embedding speaker, cross-lingua


def _load_wav_16k_mono(path):
    with wave.open(str(path), "rb") as w:
        assert w.getframerate() == 16000 and w.getnchannels() == 1, "atteso wav 16kHz mono"
        raw = w.readframes(w.getnframes())
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def run(wav_path, cfg, preset=None, num_speakers=None):
    d = cfg["diarization"]
    preset = preset or d.get("preset", "riunione")
    p = d[preset]
    n = num_speakers if num_speakers is not None else p.get("num_speakers")

    config = sherpa_onnx.OfflineSpeakerDiarizationConfig(
        segmentation=sherpa_onnx.OfflineSpeakerSegmentationModelConfig(
            pyannote=sherpa_onnx.OfflineSpeakerSegmentationPyannoteModelConfig(model=SEG_MODEL),
        ),
        embedding=sherpa_onnx.SpeakerEmbeddingExtractorConfig(model=EMB_MODEL),
        clustering=sherpa_onnx.FastClusteringConfig(
            num_clusters=int(n) if n else -1,
            threshold=float(p["cluster_threshold"]),
        ),
        min_duration_on=0.3,
        min_duration_off=0.5,
    )
    sd = sherpa_onnx.OfflineSpeakerDiarization(config)
    samples = _load_wav_16k_mono(wav_path)
    segments = sd.process(samples).sort_by_start_time()
    return [
        {"start": float(s.start), "end": float(s.end), "speaker": f"Speaker {s.speaker + 1}"}
        for s in segments
    ]
