"""Normalizzazione: qualsiasi audio o video in ingresso -> wav 16kHz mono 16-bit."""
import subprocess
import wave

import numpy as np
import imageio_ffmpeg

SAMPLE_RATE = 16000


def normalize(src, dst):
    """ffmpeg estrae/decodifica la traccia audio (mp3, m4a, aac, ogg, wav, mp4, mkv, ...)."""
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ff, "-y", "-i", str(src), "-vn", "-ac", "1", "-ar", str(SAMPLE_RATE),
         "-c:a", "pcm_s16le", str(dst)],
        check=True, capture_output=True,
    )
    return dst


def load_wav(path):
    """wav 16kHz mono 16-bit -> np.float32 in [-1, 1]. Evita che le librerie a valle
    invochino un ffmpeg di sistema che qui non esiste."""
    with wave.open(str(path), "rb") as w:
        assert w.getframerate() == SAMPLE_RATE and w.getnchannels() == 1, "atteso wav 16kHz mono"
        raw = w.readframes(w.getnframes())
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
