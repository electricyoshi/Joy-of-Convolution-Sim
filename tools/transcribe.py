"""Transcribe the original JHU narration MP3s with faster-whisper (local, GPU).

Run with the system Python 3.13 that has faster-whisper installed (``py`` defaults to 3.14,
which does not):

    C:\\Users\\Jon\\AppData\\Local\\Programs\\Python\\Python313\\python.exe tools\\transcribe.py

Reads reference/{ct,dt}/{welcome,exercises}.mp3 and writes raw transcripts, with segment
timestamps so Jon can spot-check against the audio, to reference/transcripts/. They stay under
reference/ (gitignored) because the narration is JHU's copyrighted material.

``--pass2`` re-runs with ``condition_on_previous_text=False`` and the VAD filter on, and writes ``*_pass2.txt``. The
default pass can loop or invent sentences once it mishears one (seen in ct_exercises around
1:21 and 2:20-2:52); not feeding the previous text back in stops that, at some cost in
punctuation. Compare both passes when cleaning up a transcript.
"""
import os
import sys
from pathlib import Path

from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "reference"
OUT = REF / "transcripts"

# Domain vocabulary nudges Whisper toward the right spellings ("x of t" not "X-ofty").
PROMPT = ("The Joy of Convolution. Convolution integral, convolution sum, linear time-invariant "
          "system, impulse response h of t, input x of t, output y of t, x of t minus v, h of v, "
          "integrand, unit pulse, x of n minus k, h of k, applet, decay, double pulse.")


def stamp(sec: float) -> str:
    return f"{int(sec // 60):02d}:{sec % 60:05.2f}"


def main() -> None:
    pass2 = "--pass2" in sys.argv[1:]
    OUT.mkdir(exist_ok=True)
    model = WhisperModel("large-v3", device="cuda", compute_type="float16")
    for version in ("ct", "dt"):
        for clip in ("welcome", "exercises"):
            src = REF / version / f"{clip}.mp3"
            segments, info = model.transcribe(str(src), language="en", beam_size=5,
                                              initial_prompt=PROMPT, vad_filter=pass2,
                                              condition_on_previous_text=not pass2)
            lines = [f"# {version}/{clip}.mp3  ({info.duration:.1f} s)", ""]
            for s in segments:
                lines.append(f"[{stamp(s.start)} - {stamp(s.end)}] {s.text.strip()}")
            dest = OUT / f"{version}_{clip}{'_pass2' if pass2 else ''}.txt"
            dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
            print(f"wrote {dest.relative_to(ROOT)} ({info.duration:.1f} s audio)", flush=True)


if __name__ == "__main__":
    main()
    # CTranslate2's CUDA teardown can crash the interpreter at exit on Windows (exit code 1,
    # lost buffered output) after every file is already written. Skip teardown explicitly.
    os._exit(0)
