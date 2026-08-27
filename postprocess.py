"""Post-elaborazione su misura per lezioni e riunioni.

Tutto euristico e guidato da config.yaml. Nessun modello ML qui.
ponytail: se la precisione di sezioni / action item si rivela scarsa, il punto di
upgrade e' un singolo passaggio LLM locale (es. mlx-lm) su queste due funzioni.
"""
import re


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


def run(segments, cfg, language="it"):
    pp = cfg["postprocess"]
    for s in segments:
        s["text"] = _clean_fillers(s["text"], pp["fillers"])
    segments = [s for s in segments if s["text"]]

    return {
        "language": language,
        "segments": segments,
        "sections": _split_sections(segments, pp["section_gap_seconds"], pp["section_keywords"]),
        "action_items": _extract(segments, pp["actionitem_triggers"]),
        "decisions": _extract(segments, pp["decision_triggers"]),
    }
