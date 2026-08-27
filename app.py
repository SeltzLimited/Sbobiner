"""Server locale: apre il browser, riceve l'audio in drag&drop, restituisce la trascrizione.

Uso quotidiano: doppio click su start.command. Tutto offline.
"""
import threading
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


def _pipeline(job_id, src, opts):
    j = jobs[job_id]
    try:
        wav = WORK / f"{job_id}.wav"
        j["stage"] = "Normalizzazione audio"
        audio.normalize(src, wav)

        j["stage"] = "Trascrizione (Whisper)"
        segments = transcribe.run(wav, CFG, language=opts["language"])

        if opts["diarize"]:
            j["stage"] = "Riconoscimento di chi parla"
            turns = diarize.run(wav, CFG, preset=opts["preset"], num_speakers=opts["num_speakers"])
            segments = merge.assign_speakers(segments, turns)

        j["stage"] = "Post-elaborazione"
        lang = opts["language"] if opts["language"] != "auto" else CFG.get("language", "it")
        j["result"] = postprocess.run(segments, CFG, language=lang, mode=opts["mode"])
        j["mode"] = opts["mode"]
        j["state"] = "done"
        j["stage"] = "Completato"
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
    src = WORK / f"{job_id}_{Path(f.filename).name}"
    f.save(src)
    ns = request.form.get("num_speakers", "").strip()
    opts = {
        "language": request.form.get("language", CFG.get("language", "it")),
        "mode": request.form.get("mode", "lezione"),
        "diarize": request.form.get("diarize") == "on",
        "preset": request.form.get("preset", CFG["diarization"].get("preset", "riunione")),
        "num_speakers": int(ns) if ns.isdigit() else None,
    }
    jobs[job_id] = {"state": "running", "stage": "In coda"}
    threading.Thread(target=_pipeline, args=(job_id, src, opts), daemon=True).start()
    return jsonify(job_id=job_id)


@app.get("/status/<job_id>")
def status(job_id):
    j = jobs.get(job_id)
    if not j:
        return jsonify(state="error", error="job sconosciuto"), 404
    return jsonify(state=j["state"], stage=j.get("stage", ""), error=j.get("error", ""))


@app.get("/download/<job_id>.<fmt>")
def download(job_id, fmt):
    j = jobs.get(job_id)
    if not j or j["state"] != "done":
        return "non pronto", 409
    if fmt not in ("txt", "srt", "vtt", "docx"):
        return "formato non valido", 400
    out = WORK / f"{job_id}.{fmt}"
    export.write(j["result"], fmt, out, source_name=job_id, mode=j["mode"])
    return send_file(out, as_attachment=True, download_name=f"trascrizione.{fmt}")


if __name__ == "__main__":
    url = "http://127.0.0.1:5000"
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    print(f"\n  Sbobiner attivo:  {url}\n  (chiudi questa finestra per fermare)\n")
    app.run(host="127.0.0.1", port=5000, use_reloader=False)
