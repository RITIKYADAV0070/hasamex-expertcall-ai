
import re
from pathlib import Path

TS = re.compile(r"^(\d{2}:\d{2})$")
HEADER = re.compile(r"^Expert \d+ – (.+)$")

def parse_transcript(path: str, transcript_id: str, market: str, role: str):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    expert = ""
    chunks = []
    current_ts = None
    current_speaker = None
    current_text = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        m = HEADER.match(line)
        if m:
            expert = m.group(1)
            continue
        if line.startswith("Role:"):
            role = line.split(":",1)[1].strip()
            continue
        if line.startswith("Market:"):
            market = line.split(":",1)[1].strip()
            continue
        m = TS.match(line)
        if m:
            if current_text and current_ts:
                chunks.append({
                    "id": f"{transcript_id}_{current_ts.replace(':','')}_{len(chunks)}",
                    "transcript_id": transcript_id,
                    "expert": expert,
                    "role": role,
                    "market": market,
                    "timestamp": current_ts,
                    "speaker": current_speaker,
                    "text": " ".join(current_text).strip(),
                })
            current_ts = m.group(1)
            current_text = []
            current_speaker = None
            continue
        if ":" in line and (line.startswith("Interviewer:") or line.startswith("Dr.") or line.startswith("Anna Keller:")):
            speaker, text = line.split(":",1)
            current_speaker = speaker.strip()
            current_text.append(text.strip())
        elif current_ts:
            current_text.append(line)

    if current_text and current_ts:
        chunks.append({
            "id": f"{transcript_id}_{current_ts.replace(':','')}_{len(chunks)}",
            "transcript_id": transcript_id,
            "expert": expert,
            "role": role,
            "market": market,
            "timestamp": current_ts,
            "speaker": current_speaker,
            "text": " ".join(current_text).strip(),
        })
    return chunks
