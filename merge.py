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
