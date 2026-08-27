"""Post-elaborazione su misura per lezioni e riunioni.

Tutto euristico e guidato da config.yaml. Nessun modello ML qui.
ponytail: se la precisione di sezioni / action item si rivela scarsa, il punto di
upgrade e' un singolo passaggio LLM locale (es. mlx-lm) su queste due funzioni.
"""
import re

import merge


def _apply_corrections(text, corrections):
    for wrong, right in (corrections or {}).items():
        text = re.sub(rf"\b{re.escape(wrong)}\b", right, text, flags=re.IGNORECASE)
    return text


def _clean_fillers(text, fillers):
    if not fillers:
        return text
    pattern = r"\b(" + "|".join(re.escape(f.rstrip("?")) for f in fillers) + r")\b[?,]?"
    out = re.sub(pattern, "", text, flags=re.IGNORECASE)
    out = re.sub(r"\s{2,}", " ", out)
    out = re.sub(r"\s+([.,;:!?])", r"\1", out)
    out = re.sub(r"^[\s,;:]+", "", out)
    return out.strip()


def _starts_or_contains(text, phrases):
    low = text.lower()
    return any(p in low for p in phrases)


def _split_sections(segments, gap, keywords):
    sections, cur = [], None
    prev_end = None
    for s in segments:
        boundary = (
            cur is None
            or (prev_end is not None and s["start"] - prev_end >= gap)
            or _starts_or_contains(s["text"], keywords)
        )
        if boundary:
            cur = {"index": len(sections) + 1, "start": s["start"], "end": s["end"], "segments": []}
            sections.append(cur)
        cur["segments"].append(s)
        cur["end"] = s["end"]
        prev_end = s["end"]
    return sections


def _extract(segments, triggers):
    hits = []
    for s in segments:
        if _starts_or_contains(s["text"], triggers):
            hits.append({"text": s["text"], "speaker": s.get("speaker", ""), "start": s["start"]})
    return hits


def run(segments, cfg, language="it", mode="lezione"):
    pp = cfg["postprocess"]
    corrections = cfg.get("corrections")
    for s in segments:
        s["text"] = _clean_fillers(_apply_corrections(s["text"], corrections), pp["fillers"])
    segments = [s for s in segments if s["text"]]

    # action item / decisioni sono un concetto da riunione: in "lezione" i trigger
    # ("dobbiamo", "bisogna") sono quasi sempre falsi positivi retorici.
    meeting = mode == "riunione"
    sections = _split_sections(segments, pp["section_gap_seconds"], pp["section_keywords"])
    # la trascrizione e' testo continuo per turno di parola: i segmenti brevi di
    # Whisper vengono uniti, l'intestazione (speaker + tempo) cambia solo a cambio speaker.
    para_gap = pp.get("paragraph_gap_seconds", 1.0)
    for sec in sections:
        sec["turns"] = merge.group_turns(sec.pop("segments"), para_gap)

    return {
        "language": language,
        "segments": segments,  # granulari e con i tempi: servono a SRT/VTT
        "sections": sections,
        "action_items": _extract(segments, pp["actionitem_triggers"]) if meeting else [],
        "decisions": _extract(segments, pp["decision_triggers"]) if meeting else [],
    }
