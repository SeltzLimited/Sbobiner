"""Allinea i segmenti di trascrizione ai turni di parola: chi ha detto cosa."""


def assign_speakers(segments, turns):
    """Ogni segmento prende lo speaker con cui si sovrappone di piu' nel tempo."""
    # ponytail: O(n*m). Per una lezione (~qualche migliaio di segmenti, ~centinaia di
    # turni) e' istantaneo. Se un giorno servisse, ordina i turni e fai una sweep line.
    for s in segments:
        best_speaker, best_overlap = None, 0.0
        for t in turns:
            overlap = min(s["end"], t["end"]) - max(s["start"], t["start"])
            if overlap > best_overlap:
                best_overlap, best_speaker = overlap, t["speaker"]
        s["speaker"] = best_speaker or "Speaker 1"
    return segments


def group_turns(segments, para_gap=1.0):
    """Segmenti consecutivi dello stesso speaker -> un turno di parola con testo continuo.
    Dentro il turno, una pausa piu' lunga di para_gap apre un nuovo paragrafo: cosi' il
    discorso si legge in modo naturale, senza un timestamp per ogni frase."""
    turns = []
    for s in segments:
        spk = s.get("speaker")
        if not turns or turns[-1]["speaker"] != spk:
            turns.append({"speaker": spk, "start": s["start"], "end": s["end"], "paras": [s["text"]]})
            continue
        t = turns[-1]
        if s["start"] - t["end"] > para_gap:
            t["paras"].append(s["text"])
        else:
            t["paras"][-1] = (t["paras"][-1] + " " + s["text"]).strip()
        t["end"] = s["end"]
    return turns
