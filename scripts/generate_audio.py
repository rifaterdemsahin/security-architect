#!/usr/bin/env python3
"""Generate question and answer audio for index.html with Xiaomi MiMo TTS.

Reads the `rawQuestions` array straight out of index.html, strips the HTML
from each answer, and writes two MP3s per question into audio/:

    audio/q{id}-question.mp3
    audio/q{id}-answer.mp3

The MiMo API key is pulled from Azure Key Vault `dp-kv-deliverypilot`
(secret `live-asistant-xiamimimo`) via the `az` CLI, so you must be logged in
to the info@deliverypilot.net tenant (`az login`). Set XIAOMI_MIMO_API_KEY to
skip the vault lookup.

Usage:
    python3 scripts/generate_audio.py              # generate missing files
    python3 scripts/generate_audio.py --force      # regenerate everything
    python3 scripts/generate_audio.py --ids 1 5 7  # only these questions

Requires only the Python standard library plus ffmpeg (PCM -> MP3).
"""

import argparse
import base64
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = ROOT / "index.html"
AUDIO_DIR = ROOT / "audio"

VAULT_NAME = "dp-kv-deliverypilot"
SECRET_NAME = "live-asistant-xiamimimo"

BASE_URL = os.environ.get("XIAOMI_MIMO_BASE_URL", "https://api.xiaomimimo.com/v1").rstrip("/")
TTS_MODEL = os.environ.get("MIMO_TTS_MODEL", "mimo-v2.5-tts")
SAMPLE_RATE = 24000  # MiMo returns raw little-endian PCM16, mono, 24 kHz

QUESTION_VOICE = "Dean"
ANSWER_VOICE = "Mia"


# --------------------------------------------------------------------------
# Secrets
# --------------------------------------------------------------------------
def get_api_key() -> str:
    key = os.environ.get("XIAOMI_MIMO_API_KEY")
    if key:
        return key.strip()
    try:
        out = subprocess.run(
            ["az", "keyvault", "secret", "show", "--vault-name", VAULT_NAME,
             "--name", SECRET_NAME, "--query", "value", "-o", "tsv"],
            check=True, capture_output=True, text=True,
        )
    except FileNotFoundError:
        sys.exit("Azure CLI (az) not found. Install it or set XIAOMI_MIMO_API_KEY.")
    except subprocess.CalledProcessError as e:
        sys.exit(f"Could not read {SECRET_NAME} from {VAULT_NAME}. Run `az login`.\n{e.stderr}")
    return out.stdout.strip()


# --------------------------------------------------------------------------
# Question extraction
# --------------------------------------------------------------------------
class _TextExtractor(HTMLParser):
    """Flattens answer HTML into speakable sentences."""

    BLOCK_TAGS = {"p", "li", "div", "br", "ul", "ol", "h1", "h2", "h3", "h4", "tr"}

    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)


def html_to_speech_text(fragment: str) -> str:
    parser = _TextExtractor()
    parser.feed(fragment)
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in "".join(parser.parts).split("\n")]
    lines = [ln for ln in lines if ln]
    # Make sure each bullet ends with punctuation so the voice pauses between them.
    lines = [ln if ln[-1] in ".!?:;" else ln + "." for ln in lines]
    return html.unescape(" ".join(lines))


def load_questions():
    src = INDEX_HTML.read_text(encoding="utf-8")
    start = src.index("const rawQuestions = [")
    end = src.index("];", start)
    block = src[start:end]
    pattern = re.compile(
        r'id:\s*(\d+),.*?title:\s*"((?:[^"\\]|\\.)*)".*?answer:\s*`(.*?)`',
        re.DOTALL,
    )
    questions = []
    for m in pattern.finditer(block):
        qid = int(m.group(1))
        title = json.loads(f'"{m.group(2)}"')
        questions.append({
            "id": qid,
            "question": title,
            "answer": html_to_speech_text(m.group(3)),
        })
    if not questions:
        sys.exit("No questions found in index.html")
    return questions


# --------------------------------------------------------------------------
# MiMo TTS
# --------------------------------------------------------------------------
def synthesize(text: str, voice: str, api_key: str, retries: int = 3) -> bytes:
    """Return raw PCM16 audio for `text`."""
    body = json.dumps({
        "model": TTS_MODEL,
        # MiMo TTS reads the text to speak from an assistant message.
        "messages": [{"role": "assistant", "content": text}],
        "audio": {"format": "pcm16", "voice": voice},
        "stream": True,
    }).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(1, retries + 1):
        try:
            pcm = bytearray()
            with urllib.request.urlopen(req, timeout=300) as res:
                for raw in res:
                    line = raw.decode("utf-8", "ignore").strip()
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    choices = chunk.get("choices") or [{}]
                    b64 = ((choices[0].get("delta") or {}).get("audio") or {}).get("data")
                    if b64:
                        pcm += base64.b64decode(b64)
            if not pcm:
                raise RuntimeError("MiMo returned no audio")
            return bytes(pcm)
        except (urllib.error.URLError, RuntimeError, TimeoutError) as e:
            detail = e.read().decode()[:500] if isinstance(e, urllib.error.HTTPError) else str(e)
            if attempt == retries:
                raise RuntimeError(f"TTS failed after {retries} attempts: {detail}") from e
            print(f"    retry {attempt}: {detail}")
            time.sleep(2 * attempt)


def pcm_to_mp3(pcm: bytes, out_path: Path):
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-f", "s16le", "-ar", str(SAMPLE_RATE), "-ac", "1", "-i", "pipe:0",
         "-codec:a", "libmp3lame", "-b:a", "64k", str(out_path)],
        input=pcm, check=True,
    )


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="regenerate files that already exist")
    ap.add_argument("--ids", type=int, nargs="*", help="only generate these question ids")
    args = ap.parse_args()

    questions = load_questions()
    if args.ids:
        questions = [q for q in questions if q["id"] in set(args.ids)]

    AUDIO_DIR.mkdir(exist_ok=True)
    api_key = get_api_key()

    print(f"Generating audio for {len(questions)} questions with {TTS_MODEL}")
    for q in questions:
        for kind, text, voice in (
            ("question", q["question"], QUESTION_VOICE),
            ("answer", q["answer"], ANSWER_VOICE),
        ):
            out = AUDIO_DIR / f"q{q['id']}-{kind}.mp3"
            if out.exists() and not args.force:
                print(f"  skip  {out.name}")
                continue
            print(f"  tts   {out.name} ({len(text)} chars, voice {voice})")
            pcm_to_mp3(synthesize(text, voice, api_key), out)
    print("Done.")


if __name__ == "__main__":
    main()
