import os
import json
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

SYSTEM = """You are an evidence-grounded expert interview analyst.

Use ONLY the supplied evidence.
Do not invent facts, quotes, names, markets, or timestamps.

Every substantive claim must be supported by supplied evidence.
Quotes must be copied verbatim from the supplied evidence.

If the evidence is insufficient, explicitly say that.
"""


def generate(question, evidence):
    if not evidence:
        return {
            "answer": "I could not find enough directly matching evidence in the supplied transcripts to answer reliably.",
            "evidence_ids": []
        }

    # ---------------------------------------------------------
    # FREE / OFFLINE MODE
    # ---------------------------------------------------------
    # Unless explicitly enabled, do not call any paid API.
    use_openai = os.getenv("USE_OPENAI", "false").lower() == "true"

    if not use_openai:
        return deterministic_answer(question, evidence)

    # ---------------------------------------------------------
    # OPTIONAL OPENAI MODE
    # ---------------------------------------------------------
    try:
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            return deterministic_answer(question, evidence)

        client = OpenAI(api_key=api_key)

        payload = [
            {
                "id": e["id"],
                "expert": e["expert"],
                "market": e["market"],
                "timestamp": e["timestamp"],
                "text": e["text"]
            }
            for e in evidence
        ]

        prompt = (
            f"QUESTION:\n{question}\n\n"
            f"EVIDENCE:\n{json.dumps(payload, ensure_ascii=False)}"
        )

        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt}
            ]
        )

        return json.loads(resp.choices[0].message.content)

    except Exception:
        # If API is unavailable / has no credits / fails,
        # automatically fall back to the free evidence mode.
        return deterministic_answer(question, evidence)


def deterministic_answer(question, evidence):
    """
    Free, deterministic answer generator.

    It does not invent a conclusion using an LLM.
    Instead it organizes the retrieved transcript evidence
    by market/expert and surfaces the relevant source text.
    """

    question_lower = question.lower()

    # Group evidence by market
    grouped = {}

    for item in evidence:
        market = item.get("market", "Unknown market")
        grouped.setdefault(market, []).append(item)

    sections = []

    for market, items in grouped.items():
        lines = []

        for item in items:
            expert = item.get("expert", "Expert")
            timestamp = item.get("timestamp", "")
            text = item.get("text", "")

            lines.append(
                f"{expert} ({timestamp}): {text}"
            )

        sections.append(
            f"{market}:\n" + "\n".join(lines)
        )

    # Question-aware introduction
    if "roi" in question_lower or "return" in question_lower or "budget" in question_lower:
        intro = (
            "Across the retrieved interviews, ROI and economic considerations "
            "are discussed in relation to purchasing decisions. The evidence below "
            "shows how each market describes those considerations."
        )

    elif "training" in question_lower:
        intro = (
            "The retrieved interviews discuss training as an important factor "
            "in adoption and utilization. The source evidence is shown below."
        )

    elif "timeline" in question_lower or "purchase" in question_lower:
        intro = (
            "The retrieved interviews describe different purchasing timelines "
            "and the factors affecting them. The source evidence is shown below."
        )

    elif "adoption" in question_lower:
        intro = (
            "The retrieved interviews describe adoption patterns across the "
            "markets. The source evidence is shown below."
        )

    else:
        intro = (
            "The following answer is based directly on the retrieved transcript "
            "evidence. No unsupported claims have been added."
        )

    answer = intro + "\n\n" + "\n\n".join(sections)

    return {
        "answer": answer,
        "evidence_ids": [x["id"] for x in evidence]
    }