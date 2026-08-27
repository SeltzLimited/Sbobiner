"""Normalizzazione: qualsiasi audio o video in ingresso -> wav 16kHz mono 16-bit."""
import subprocess
import imageio_ffmpeg


def normalize(src, dst):
    """ffmpeg estrae/decodifica la traccia audio (mp3, m4a, aac, ogg, wav, mp4, mkv, ...)."""
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ff, "-y", "-i", str(src), "-vn", "-ac", "1", "-ar", "16000",
         "-c:a", "pcm_s16le", str(dst)],
        check=True, capture_output=True,
    )
    return dst
