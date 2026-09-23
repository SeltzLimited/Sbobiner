"""Server locale: apre il browser, riceve l'audio in drag&drop, restituisce la trascrizione.

Uso quotidiano: doppio click su start.command (Mac) o start.bat (Windows). Tutto offline.
"""
import logging
import os
import re
import subprocess
import sys
import threading
import time
import traceback
import uuid
from pathlib import Path

import webbrowser
import yaml
from flask import Flask, jsonify, render_template, request, send_file

import audio
import transcribe
import diarize
import merge
import postprocess
import export

ROOT = Path(__file__).parent
WORK = ROOT / "work"
WORK.mkdir(exist_ok=True)
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())

app = Flask(__name__)
jobs = {}  # ponytail: dict in-process, 1 utente locale. Se diventasse multiutente: coda vera.

LANGUAGES = [("it", "Italiano"), ("auto", "Rileva automaticamente"), ("en", "Inglese"),
             ("fr", "Francese"), ("de", "Tedesco"), ("es", "Spagnolo")]


def _ramp(j, lo, hi, est_seconds, stop):
    """Fa avanzare la barra durante una fase senza callback (la trascrizione),
    in base a una stima di durata. Si ferma quando `stop` viene settato."""
    t0 = time.time()
    while not stop.wait(0.7):
        frac = min(0.97, (time.time() - t0) / max(est_seconds, 1))
        j["progress"] = int(lo + (hi - lo) * frac)


def _pipeline(job_id, src, opts):
    j = jobs[job_id]

    def stage(text, pct):
        j["stage"], j["progress"] = text, int(pct)

    try:
        wav = WORK / f"{job_id}.wav"
        stage("Preparazione dell'audio", 1)
        audio.normalize(src, wav)
        secs = audio.duration(wav)

        # ripartizione della barra: trascrizione la fetta grande, diarization se attiva
        tr_hi = 55 if opts["diarize"] else 90
        stage("Trascrizione in corso", 4)

        def tr_progress(frac):
            j["progress"] = int(4 + (tr_hi - 4) * frac)

        stop = threading.Event()
        if not transcribe.REPORTS_PROGRESS:  # mlx-whisper non dice a che punto e': stima a tempo
            threading.Thread(target=_ramp, args=(j, 4, tr_hi, secs / 8.0, stop), daemon=True).start()
        try:
            segments = transcribe.run(wav, CFG, language=opts["language"], progress=tr_progress)
        finally:
            stop.set()
        j["progress"] = tr_hi

        if opts["diarize"]:
            stage("Riconoscimento di chi parla", tr_hi)

            def diar_progress(frac):
                j["progress"] = int(tr_hi + (90 - tr_hi) * frac)

            turns = diarize.run(wav, CFG, preset=opts["preset"],
                                num_speakers=opts["num_speakers"], progress=diar_progress)
            segments = merge.assign_speakers(segments, turns)
            j["progress"] = 90

        stage("Pulizia e organizzazione del testo", 94)
        lang = opts["language"] if opts["language"] != "auto" else CFG.get("language", "it")
        j["result"] = postprocess.run(segments, CFG, language=lang, mode=opts["mode"])
        j["mode"] = opts["mode"]
        stage("Completato", 100)
        j["state"] = "done"
    except Exception as e:
        j["state"] = "error"
        j["error"] = f"{e}\n{traceback.format_exc()}"


@app.route("/")
def index():
    return render_template(
        "index.html",
        languages=LANGUAGES,
        default_language=CFG.get("language", "it"),
        default_preset=CFG["diarization"].get("preset", "riunione"),
    )


@app.post("/transcribe")
def start():
    f = request.files["audio"]
    job_id = uuid.uuid4().hex[:12]
    # nome breve e senza caratteri strani: evita i limiti di lunghezza/caratteri dei percorsi Windows
    suffix = re.sub(r"[^A-Za-z0-9.]", "", Path(f.filename or "").suffix)[:10]
    src = WORK / f"{job_id}{suffix}"
    f.save(src)
    name = Path(f.filename or "").stem or "trascrizione"  # nome dei file scaricati
    ns = request.form.get("num_speakers", "").strip()
    opts = {
        "language": request.form.get("language", CFG.get("language", "it")),
        "mode": request.form.get("mode", "lezione"),
        "diarize": request.form.get("diarize") == "on",
        "preset": request.form.get("preset", CFG["diarization"].get("preset", "riunione")),
        "num_speakers": int(ns) if ns.isdigit() else None,
    }
    jobs[job_id] = {"state": "running", "stage": "In coda", "progress": 0, "name": name}
    threading.Thread(target=_pipeline, args=(job_id, src, opts), daemon=True).start()
    return jsonify(job_id=job_id)


@app.get("/status/<job_id>")
def status(job_id):
    j = jobs.get(job_id)
    if not j:
        return jsonify(state="error", error="job sconosciuto"), 404
    return jsonify(state=j["state"], stage=j.get("stage", ""),
                   progress=j.get("progress", 0), error=j.get("error", ""))


@app.get("/download/<job_id>.<fmt>")
def download(job_id, fmt):
    j = jobs.get(job_id)
    if not j or j["state"] != "done":
        return "non pronto", 409
    if fmt not in ("txt", "srt", "vtt", "docx"):
        return "formato non valido", 400
    name = j.get("name", "trascrizione")
    out = WORK / f"{job_id}.{fmt}"
    export.write(j["result"], fmt, out, source_name=name, mode=j["mode"])
    return send_file(out, as_attachment=True, download_name=f"{name}.{fmt}")


def _open_ui(url):
    """Windows: finestra "app" di Edge, o di Chrome se Edge manca (niente schede ne' barra
    degli indirizzi). Altrove, o se non trova nessuno dei due: browser predefinito."""
    if sys.platform == "win32":
        bases = [os.environ.get(k) for k in ("ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA")]
        for rel in (r"Microsoft\Edge\Application\msedge.exe", r"Google\Chrome\Application\chrome.exe"):
            for base in filter(None, bases):
                exe = Path(base) / rel
                if exe.exists():
                    subprocess.Popen([str(exe), f"--app={url}"])
                    return
    webbrowser.open(url)


if __name__ == "__main__":
    # niente log per ogni richiesta: su Windows, un click nella finestra nera sospende
    # l'output e con lui il server, che scrive a ogni aggiornamento della barra.
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    url = "http://127.0.0.1:5000"
    threading.Timer(1.0, lambda: _open_ui(url)).start()
    print(f"\n  Sbobiner attivo:  {url}\n  (chiudi questa finestra per fermare)\n")
    app.run(host="127.0.0.1", port=5000, use_reloader=False)
