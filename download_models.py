"""Scarica una volta i modelli (Whisper + diarization) nella cartella models/.
Dopo questo, il sistema gira completamente offline.
"""
import shutil
import ssl
import sys
import tarfile
import urllib.request
from pathlib import Path

import certifi
import yaml

# Python di python.org non usa i certificati di sistema: prendiamo la CA bundle da certifi.
_SSL = ssl.create_default_context(cafile=certifi.where())

ROOT = Path(__file__).parent
MODELS = ROOT / "models"
MODELS.mkdir(exist_ok=True)

SEG_URL = ("https://github.com/k2-fsa/sherpa-onnx/releases/download/"
           "speaker-segmentation-models/sherpa-onnx-pyannote-segmentation-3-0.tar.bz2")
# NB: il tag della release upstream contiene un refuso ("recongition"), non correggerlo.
EMB_URL = ("https://github.com/k2-fsa/sherpa-onnx/releases/download/"
           "speaker-recongition-models/wespeaker_en_voxceleb_CAM++.onnx")


def _download(url, dst):
    if dst.exists():
        print(f"  gia' presente: {dst.name}")
        return
    print(f"  scarico: {url.split('/')[-1]}")
    req = urllib.request.Request(url, headers={"User-Agent": "trascrizione-offline"})
    with urllib.request.urlopen(req, context=_SSL) as r, open(dst, "wb") as f:
        shutil.copyfileobj(r, f)


def diarization_models():
    tar = MODELS / "seg.tar.bz2"
    if not (MODELS / "sherpa-onnx-pyannote-segmentation-3-0" / "model.onnx").exists():
        _download(SEG_URL, tar)
        with tarfile.open(tar, "r:bz2") as t:
            t.extractall(MODELS, filter="data")
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
