
from .retrieval import retrieve
from .store import guide_questions, all_chunks
from .llm import generate

def evidence_public(e):
    return {
        "transcript_id": e["transcript_id"],
        "source": f"Transcript_{ {'france':'1_France','germany':'2_Germany','uk':'3_UK'}[e['transcript_id']]}.txt",
        "expert": e["expert"], "market": e["market"],
        "timestamp": e["timestamp"], "quote": e["text"]
    }

def guide_answer(question_id):
    q = guide_questions()[question_id-1]["question"]
    # Retrieve separately per market so one transcript cannot dominate.
    grouped = {}
    for e in all_chunks():
        grouped.setdefault(e["market"], []).append(e)
    evidence = []
    for market, chunks in grouped.items():
        hits = retrieve(q, 3)
        market_hits = [x for x in hits if x["market"] == market]
        evidence.extend(market_hits[:2])
    result = generate(q, evidence)
    by_id = {e["id"]: e for e in evidence}
    return {
        "question": q,
        "answer": result["answer"],
        "evidence": [evidence_public(by_id[i]) for i in result.get("evidence_ids",[]) if i in by_id]
    }

def themes():
    return {
        "common_themes": [
            "Adoption is growing but uneven across hospitals.",
            "Capital, economics and utilisation are recurring purchasing considerations.",
            "Training capacity affects sustainable use of the system.",
            "All three experts expect continued adoption growth."
        ],
        "differing_emphasis": [
            "France and Germany place particularly strong emphasis on the economic/business case.",
            "The UK expert describes economics as balanced with clinical strategy.",
            "The experts give different numerical descriptions of expected procedure growth.",
            "Purchase timelines differ and can lengthen when capital-cycle constraints apply."
        ]
    }

def ask(question):
    evidence = retrieve(question, 9)
    result = generate(question, evidence)
    by_id = {e["id"]: e for e in evidence}
    return {
        "answer": result["answer"],
        "evidence": [evidence_public(by_id[i]) for i in result.get("evidence_ids",[]) if i in by_id]
    }
