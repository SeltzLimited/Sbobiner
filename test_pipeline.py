"""Self-check: python test_pipeline.py  (nessun framework, solo assert)."""
import merge
import postprocess

CFG = {
    "postprocess": {
        "fillers": ["ehm", "cioè", "no?"],
        "section_gap_seconds": 4.0,
        "section_keywords": ["passiamo a"],
        "actionitem_triggers": ["dobbiamo", "entro il"],
        "decision_triggers": ["abbiamo deciso"],
    }
}


def test_merge_picks_max_overlap():
    segs = [{"start": 0.0, "end": 2.0, "text": "a"}, {"start": 5.0, "end": 7.0, "text": "b"}]
    turns = [
        {"start": 0.0, "end": 3.0, "speaker": "Speaker 1"},
        {"start": 3.0, "end": 10.0, "speaker": "Speaker 2"},
    ]
    out = merge.assign_speakers(segs, turns)
    assert out[0]["speaker"] == "Speaker 1"
    assert out[1]["speaker"] == "Speaker 2"


def test_merge_no_overlap_defaults():
    segs = [{"start": 100.0, "end": 101.0, "text": "x"}]
    out = merge.assign_speakers(segs, [{"start": 0.0, "end": 1.0, "speaker": "Speaker 1"}])
    assert out[0]["speaker"] == "Speaker 1"


def test_group_turns():
    segs = [
        {"start": 0.0, "end": 2.0, "text": "ciao", "speaker": "Speaker 1"},
        {"start": 2.1, "end": 4.0, "text": "come va", "speaker": "Speaker 1"},   # stesso spk, no gap
        {"start": 10.0, "end": 12.0, "text": "dopo pausa", "speaker": "Speaker 1"},  # stesso spk, gap
        {"start": 12.0, "end": 14.0, "text": "rispondo io", "speaker": "Speaker 2"},  # cambio spk
    ]
    turns = merge.group_turns(segs, para_gap=2.5)
    assert len(turns) == 2
    assert turns[0]["speaker"] == "Speaker 1" and turns[1]["speaker"] == "Speaker 2"
    assert turns[0]["paras"] == ["ciao come va", "dopo pausa"]
    assert turns[1]["paras"] == ["rispondo io"]


def test_group_turns_no_speaker():
    segs = [{"start": 0.0, "end": 2.0, "text": "a"}, {"start": 2.2, "end": 4.0, "text": "b"}]
    turns = merge.group_turns(segs)
    assert len(turns) == 1 and turns[0]["speaker"] is None and turns[0]["paras"] == ["a b"]


def test_fillers_removed():
    r = postprocess.run([{"start": 0.0, "end": 1.0, "text": "ehm allora cioè iniziamo no?"}], CFG)
    assert "ehm" not in r["segments"][0]["text"]
    assert "cioè" not in r["segments"][0]["text"]
    assert r["segments"][0]["text"] == "allora iniziamo"


def test_sections_split_on_gap_and_keyword():
    segs = [
        {"start": 0.0, "end": 2.0, "text": "intro"},
        {"start": 2.5, "end": 4.0, "text": "ancora intro"},
        {"start": 9.0, "end": 11.0, "text": "nuovo blocco dopo pausa"},  # gap 5s
        {"start": 11.0, "end": 13.0, "text": "passiamo a un altro tema"},  # keyword
    ]
    r = postprocess.run(segs, CFG)
    assert len(r["sections"]) == 3


def test_action_items_and_decisions():
    segs = [
        {"start": 1.0, "end": 2.0, "text": "dobbiamo mandare il report", "speaker": "Speaker 1"},
        {"start": 3.0, "end": 4.0, "text": "abbiamo deciso di rimandare", "speaker": "Speaker 2"},
        {"start": 5.0, "end": 6.0, "text": "bel tempo oggi", "speaker": "Speaker 1"},
    ]
    r = postprocess.run(segs, CFG, mode="riunione")
    assert len(r["action_items"]) == 1 and r["action_items"][0]["speaker"] == "Speaker 1"
    assert len(r["decisions"]) == 1 and r["decisions"][0]["speaker"] == "Speaker 2"
    assert postprocess.run(segs, CFG, mode="lezione")["action_items"] == []


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok  {name}")
    print("tutti i check passati")
