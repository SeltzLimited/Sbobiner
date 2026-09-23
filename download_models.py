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
    req = urllib.request.Request(url, headers={"User-Agent": "sbobiner"})
    with urllib.request.urlopen(req, context=_SSL) as r, open(dst, "wb") as f:
        shutil.copyfileobj(r, f)


def diarization_models():
    seg_dir = MODELS / "sherpa-onnx-pyannote-segmentation-3-0"
    tar = MODELS / "seg.tar.bz2"
    if not (seg_dir / "model.int8.onnx").exists():
        _download(SEG_URL, tar)
        with tarfile.open(tar, "r:bz2") as t:
            try:
                t.extractall(MODELS, filter="data")
            except TypeError:  # Python che non ha ancora il parametro filter
                t.extractall(MODELS)
        tar.unlink()
        # del tarball teniamo solo il modello che usiamo: via script, licenze, vad, fp32
        for f in seg_dir.iterdir():
            if f.name != "model.int8.onnx":
                f.unlink()
    _download(EMB_URL, MODELS / "wespeaker_en_voxceleb_CAM++.onnx")


def whisper_model():
    import transcribe
    name = yaml.safe_load((ROOT / "config.yaml").read_text())["model"]["name"]
    print(f"  scarico modello Whisper: {name}")
    snapshot = Path(transcribe.download(name))
    _offer_cleanup(snapshot.parents[1])  # .../models--org--repo/snapshots/<rev>


def _offer_cleanup(keep_dir):
    """Propone di eliminare gli altri modelli Whisper in cache (es. dopo un cambio di modello).
    Usa l'API di huggingface_hub: le versioni recenti condividono i file grossi tra
    repository, cancellare la cartella a mano non libererebbe spazio."""
    from huggingface_hub import scan_cache_dir
    cache = scan_cache_dir(keep_dir.parent)
    stale = [r for r in cache.repos
             if "whisper" in r.repo_id.lower() and r.repo_path.name != keep_dir.name]
    if not stale:
        return
    gb = sum(r.size_on_disk for r in stale) / 1e9
    print(f"  Modelli Whisper non piu' usati: {', '.join(r.repo_id for r in stale)} (~{gb:.1f} GB)")
    if not sys.stdin.isatty() or input("  Eliminarli per liberare spazio? [s/N] ").strip().lower() != "s":
        return
    cache.delete_revisions(*(rev.commit_hash for r in stale for rev in r.revisions)).execute()
    print("  Eliminati.")


if __name__ == "__main__":
    print("Modelli diarization...")
    diarization_models()
    print("Modello Whisper...")
    whisper_model()
    print("OK. Il sistema ora funziona offline.")
    sys.exit(0)
