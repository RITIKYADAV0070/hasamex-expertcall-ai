
from pathlib import Path
from .parser import parse_transcript

BASE = Path(__file__).resolve().parents[2] / "data"

SOURCES = [
    ("france", "Transcript_1_France.txt", "France", "Head of Urology"),
    ("germany", "Transcript_2_Germany.txt", "Germany", "Former Hospital Procurement Director"),
    ("uk", "Transcript_3_UK.txt", "United Kingdom", "Consultant Urologist"),
]

GUIDE = [
    "How would you describe current adoption of robotic surgery in your market?",
    "What are the main barriers to adoption?",
    "How important are hospital budgets and ROI in purchasing decisions?",
    "How important are surgeon training and clinical outcomes?",
    "What adoption trend do you expect over the next 3–5 years?",
    "What is the typical hospital decision-making timeline for purchasing a new robotic system?",
]

CHUNKS = []
for tid, filename, market, role in SOURCES:
    CHUNKS.extend(parse_transcript(str(BASE / filename), tid, market, role))

def all_chunks():
    return CHUNKS

def guide_questions():
    return [{"id": i+1, "question": q} for i, q in enumerate(GUIDE)]
