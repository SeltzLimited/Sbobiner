"""Scarica una volta i modelli (Whisper + diarization) nella cartella models/.
Dopo questo, il sistema gira completamente offline.
"""
import sys
import tarfile
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).parent
MODELS = ROOT / "models"
MODELS.mkdir(exist_ok=True)

SEG_URL = ("https://github.com/k2-fsa/sherpa-onnx/releases/download/"
           "speaker-segmentation-models/sherpa-onnx-pyannote-segmentation-3-0.tar.bz2")
EMB_URL = ("https://github.com/k2-fsa/sherpa-onnx/releases/download/"
           "speaker-recognition-models/wespeaker_en_voxceleb_CAM++.onnx")


def _download(url, dst):
    if dst.exists():
        print(f"  gia' presente: {dst.name}")
        return
    print(f"  scarico: {url.split('/')[-1]}")
    urllib.request.urlretrieve(url, dst)


def diarization_models():
    tar = MODELS / "seg.tar.bz2"
    if not (MODELS / "sherpa-onnx-pyannote-segmentation-3-0" / "model.onnx").exists():
        _download(SEG_URL, tar)
        with tarfile.open(tar, "r:bz2") as t:
            t.extractall(MODELS)
        tar.unlink()
    _download(EMB_URL, MODELS / "wespeaker_en_voxceleb_CAM++.onnx")


def whisper_model():
    from huggingface_hub import snapshot_download
    import transcribe
    repo = transcribe.repo_for(yaml.safe_load((ROOT / "config.yaml").read_text())["model"]["name"])
    print(f"  scarico modello Whisper: {repo}")
    snapshot_download(repo)


if __name__ == "__main__":
    print("Modelli diarization...")
    diarization_models()
    print("Modello Whisper...")
    whisper_model()
    print("OK. Il sistema ora funziona offline.")
    sys.exit(0)
