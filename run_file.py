"""Elabora un singolo file da riga di comando (test / uso batch).

  python run_file.py work/registrazione.m4a --mode lezione [--diarize] [--preset aula]

I segmenti grezzi (pre post-elaborazione) vengono salvati in work/<nome>.segments.json.
Per ri-provare glossario/correzioni/sezioni senza ri-trascrivere:
  python run_file.py work/registrazione.m4a --from-json --mode riunione
"""
import argparse
import json
import time
from pathlib import Path

import yaml

import audio
import transcribe
import diarize
import merge
import postprocess
import export

ROOT = Path(__file__).parent
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("--mode", default="lezione", choices=["lezione", "riunione"])
ap.add_argument("--diarize", action="store_true")
ap.add_argument("--preset", default=None)
ap.add_argument("--language", default=None)
ap.add_argument("--from-json", action="store_true",
                help="riparti dai segmenti salvati, salta normalizzazione e trascrizione")
a = ap.parse_args()

src = Path(a.src)
stem = ROOT / "work" / src.stem
raw_json = stem.with_suffix(".segments.json")
t0 = time.time()


def log(msg):
    print(f"[{time.time() - t0:6.1f}s] {msg}", flush=True)


if a.from_json:
    log(f"carico segmenti da {raw_json.name}")
    segments = json.loads(raw_json.read_text())
else:
    log("normalizzazione audio")
    wav = stem.with_suffix(".wav")
    audio.normalize(src, wav)

    log("trascrizione")
    segments = transcribe.run(wav, CFG, language=a.language)
    log(f"  {len(segments)} segmenti")

    if a.diarize:
        log("diarization")
        turns = diarize.run(wav, CFG, preset=a.preset)
        log(f"  {len(set(t['speaker'] for t in turns))} speaker, {len(turns)} turni")
        segments = merge.assign_speakers(segments, turns)

    raw_json.write_text(json.dumps(segments, ensure_ascii=False))

log("post-elaborazione")
lang = a.language if a.language and a.language != "auto" else CFG.get("language", "it")
result = postprocess.run(segments, CFG, language=lang, mode=a.mode)
log(f"  sezioni={len(result['sections'])} action={len(result['action_items'])} "
    f"decisioni={len(result['decisions'])}")

for fmt in ("txt", "srt", "vtt", "docx"):
    out = stem.with_suffix(f".{fmt}")
    export.write(result, fmt, out, source_name=src.stem, mode=a.mode)
    log(f"scritto {out.name}")

log("fatto")
