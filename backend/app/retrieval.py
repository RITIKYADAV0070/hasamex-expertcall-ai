import re

from .store import all_chunks


STOP = set("""
the a an and or to of in on for with is are was were be this that it they their
what how why when where would could should from across about do does did
are were been being
""".split())


# -------------------------------------------------------------------
# Topic vocabularies
# -------------------------------------------------------------------

CONCEPTS = {
    "adoption": {
        "adoption", "adopt", "adopting", "growing", "growth",
        "hospitals", "hospital", "centres", "centers",
        "access", "standard", "advanced", "available"
    },

    "barrier": {
        "barrier", "barriers", "holding", "slow", "slower",
        "challenge", "challenges", "issue", "issues",
        "cost", "costs", "funding", "training", "access",
        "budget", "budgets", "capital", "approval",
        "economic", "economics", "utilisation", "utilization",
        "volume", "prove", "proving"
    },

    "roi": {
        "roi", "return", "payback", "utilisation", "utilization",
        "procedure", "procedures", "volume", "maintenance",
        "finance", "financial", "economic", "economics",
        "business", "businesscase", "cost", "costs",
        "budget", "budgets", "tco", "approval", "approve",
        "pay", "pays", "investment"
    },

    "training": {
        "training", "train", "trained", "surgeon", "surgeons",
        "staff", "theatre", "utilisation", "utilization",
        "skills", "capacity", "people", "experience"
    },

    "clinical": {
        "clinical", "outcomes", "outcome", "length",
        "stay", "recruitment", "procedure", "procedures",
        "patient", "patients", "benefit", "benefits"
    },

    "purchase": {
        "purchase", "purchasing", "procurement", "approval",
        "funding", "budget", "capital", "months", "timeline",
        "cycle", "buy", "buying", "committee", "order",
        "decision", "decisions", "signed"
    },

    "outlook": {
        "outlook", "future", "expect", "expectation",
        "accelerate", "growth", "years", "procedures",
        "increase", "increasing", "continue", "continued"
    },
}


# -------------------------------------------------------------------
# Question-specific intent profiles
# -------------------------------------------------------------------

QUESTION_PROFILES = {
    "adoption": {
        "keywords": {
            "adoption", "adopt", "adopting", "growing",
            "growth", "standard", "access", "hospitals",
            "centres", "centers", "advanced"
        },
        "concepts": {"adoption"},
        "negative": {
            "budget", "roi", "training", "procurement",
            "maintenance", "payback"
        }
    },

    "barrier": {
        "keywords": {
            "barrier", "barriers", "holding", "challenge",
            "challenges", "issue", "issues", "cost", "costs",
            "funding", "budget", "capital", "approval",
            "training", "access", "utilisation", "utilization",
            "volume", "economic", "economics", "prove", "proving"
        },
        "concepts": {"barrier"},
        "negative": {
            "growing", "growth", "standard", "advanced"
        }
    },

    "roi": {
        "keywords": {
            "roi", "return", "payback", "utilisation",
            "utilization", "procedure", "procedures", "volume",
            "maintenance", "finance", "financial", "economic",
            "economics", "business", "cost", "costs",
            "budget", "budgets", "tco", "approval", "pay",
            "investment"
        },
        "concepts": {"roi"},
        "negative": {
            "growing", "growth", "future", "outlook"
        }
    },

    "training": {
        "keywords": {
            "training", "train", "trained", "surgeon",
            "surgeons", "staff", "theatre", "capacity",
            "people", "skills", "experience", "outcomes",
            "clinical", "recruitment", "length", "stay"
        },
        "concepts": {"training", "clinical"},
        "negative": {
            "budget", "procurement", "timeline", "months"
        }
    },

    "outlook": {
        "keywords": {
            "outlook", "future", "expect", "expectation",
            "accelerate", "growth", "years", "procedures",
            "increase", "increasing", "continue", "continued"
        },
        "concepts": {"outlook"},
        "negative": {
            "procurement", "months", "committee",
            "cost", "budget"
        }
    },

    "purchase": {
        "keywords": {
            "purchase", "purchasing", "procurement",
            "approval", "funding", "budget", "capital",
            "months", "timeline", "cycle", "buy", "buying",
            "committee", "order", "decision", "decisions",
            "signed"
        },
        "concepts": {"purchase"},
        "negative": {
            "growing", "growth", "outlook", "future"
        }
    },
}


def tokens(text):
    """
    Convert text into normalized tokens.
    """
    return set(
        re.findall(r"[a-z0-9]+", text.lower())
    ) - STOP


def detect_intent(query):
    """
    Determine which interview-guide intent most closely
    matches the user's question.
    """

    q = tokens(query)
    lowered = query.lower()

    # ---------------------------------------------------------------
    # Strong phrase matches
    # ---------------------------------------------------------------

    if (
        "barrier" in lowered
        or "barriers" in lowered
        or "holding adoption" in lowered
        or "holding" in lowered
    ):
        return "barrier"

    if (
        "roi" in lowered
        or "return on investment" in lowered
        or "payback" in lowered
        or "economic case" in lowered
    ):
        return "roi"

    if (
        "training" in lowered
        or "trained" in lowered
        or "surgeon training" in lowered
        or "clinical outcomes" in lowered
    ):
        return "training"

    if (
        "how long" in lowered
        or "timeline" in lowered
        or "purchase" in lowered
        or "purchasing" in lowered
        or "procurement" in lowered
        or "signed order" in lowered
    ):
        return "purchase"

    if (
        "three to five" in lowered
        or "3–5" in lowered
        or "3-5" in lowered
        or ("next" in lowered and "years" in lowered)
        or "future" in lowered
        or "outlook" in lowered
    ):
        return "outlook"

    if (
        "adoption" in lowered
        or "adopting" in lowered
        or ("current" in lowered and "market" in lowered)
    ):
        return "adoption"

    # ---------------------------------------------------------------
    # Vocabulary fallback
    # ---------------------------------------------------------------

    best_intent = None
    best_score = 0

    for intent, profile in QUESTION_PROFILES.items():

        score = len(
            q & profile["keywords"]
        )

        if score > best_score:
            best_score = score
            best_intent = intent

    return best_intent


def is_interviewer_question(text):
    """
    Questions asked by the interviewer should not be surfaced
    as substantive evidence.
    """

    stripped = text.strip()

    if not stripped:
        return True

    if stripped.endswith("?"):
        return True

    prefixes = (
        "how would you describe",
        "how important is",
        "what is holding",
        "what do you expect",
        "do you expect",
        "would you say",
        "any rough expectation",
        "so roi is important",
        "so would you say",
        "what is the main",
        "what are the main",
        "how long does",
    )

    lowered = stripped.lower()

    return any(
        lowered.startswith(prefix)
        for prefix in prefixes
    )


def score_chunk(query, chunk):
    """
    Question-aware deterministic retrieval.

    Higher scores indicate stronger relevance to the
    specific interview question.
    """

    q = tokens(query)

    text = chunk.get("text", "")
    t = tokens(text)

    if not t:
        return -999

    intent = detect_intent(query)

    if intent not in QUESTION_PROFILES:
        return len(q & t)

    profile = QUESTION_PROFILES[intent]

    score = 0

    # ---------------------------------------------------------------
    # 1. Direct query overlap
    # ---------------------------------------------------------------

    direct_overlap = len(q & t)

    score += direct_overlap * 8

    # ---------------------------------------------------------------
    # 2. Intent-specific vocabulary
    # ---------------------------------------------------------------

    keyword_matches = len(
        t & profile["keywords"]
    )

    score += min(
        keyword_matches * 4,
        28
    )

    # ---------------------------------------------------------------
    # 3. Concept vocabulary
    # ---------------------------------------------------------------

    for concept in profile["concepts"]:

        concept_words = CONCEPTS.get(
            concept,
            set()
        )

        matches = len(
            t & concept_words
        )

        if concept == "barrier":
            score += min(matches * 4, 24)

        elif concept == "roi":
            score += min(matches * 4, 24)

        elif concept == "training":
            score += min(matches * 4, 20)

        elif concept == "clinical":
            score += min(matches * 3, 12)

        elif concept == "purchase":
            score += min(matches * 4, 24)

        elif concept == "outlook":
            score += min(matches * 3, 18)

        elif concept == "adoption":
            score += min(matches * 3, 18)

    # ---------------------------------------------------------------
    # 4. Question-specific boosts
    # ---------------------------------------------------------------

    if intent == "outlook":

        outlook_terms = {
            "expect", "expected", "expectation",
            "future", "growth", "growing",
            "increase", "increasing",
            "accelerate", "continue",
            "continued", "years",
            "annual", "annually"
        }

        outlook_matches = len(
            t & outlook_terms
        )

        score += outlook_matches * 7

        # Explicit growth ranges are very strong evidence.
        if re.search(
            r"\b\d+\s*(?:to|-)\s*\d+\s*percent\b",
            text.lower()
        ):
            score += 30

        # Explicit percentage is also strong evidence.
        if re.search(
            r"\b\d+\s*percent\b",
            text.lower()
        ):
            score += 18

        # Penalize current-state answers.
        current_state_terms = {
            "standard",
            "access",
            "available",
            "selected",
            "hospital"
        }

        current_matches = len(
            t & current_state_terms
        )

        if (
            current_matches >= 3
            and outlook_matches <= 2
        ):
            score -= 25

    elif intent == "purchase":

        timeline_terms = {
            "months", "month",
            "timeline", "procurement",
            "purchase", "purchasing",
            "committee", "capital",
            "cycle", "order",
            "decision", "decisions"
        }

        timeline_matches = len(
            t & timeline_terms
        )

        score += timeline_matches * 7

        # Explicit numeric duration is extremely strong.
        if re.search(
            r"\b(?:six|nine|twelve|eighteen|6|9|12|18)"
            r"\s*(?:to|-)\s*"
            r"(?:six|nine|twelve|eighteen|6|9|12|18)"
            r"\s*months?\b",
            text.lower()
        ):
            score += 45

        # Any explicit duration in months is strong.
        if re.search(
            r"\b(?:\d+|six|nine|twelve|eighteen)"
            r"\s+months?\b",
            text.lower()
        ):
            score += 20

        # Penalize barrier-oriented answers.
        barrier_matches = len(
            t & {
                "barrier",
                "barriers",
                "cost",
                "costs",
                "proving",
                "prove",
                "issue",
                "issues"
            }
        )

        if barrier_matches >= 2:
            score -= 35

    elif intent == "training":

        training_terms = {
            "training",
            "trained",
            "surgeon",
            "surgeons",
            "staff",
            "theatre",
            "capacity",
            "utilisation",
            "utilization",
            "outcomes",
            "clinical"
        }

        score += len(
            t & training_terms
        ) * 5

    elif intent == "barrier":

        barrier_terms = {
            "barrier",
            "barriers",
            "cost",
            "costs",
            "funding",
            "budget",
            "capital",
            "approval",
            "training",
            "capacity",
            "proving",
            "utilisation",
            "utilization"
        }

        score += len(
            t & barrier_terms
        ) * 5

    elif intent == "roi":

        roi_terms = {
            "roi",
            "payback",
            "utilisation",
            "utilization",
            "procedure",
            "procedures",
            "volume",
            "maintenance",
            "finance",
            "financial",
            "economic",
            "economics",
            "tco",
            "cost",
            "budget",
            "approval"
        }

        score += len(
            t & roi_terms
        ) * 5

    elif intent == "adoption":

        adoption_terms = {
            "adoption",
            "adopt",
            "growing",
            "growth",
            "hospitals",
            "centres",
            "centers",
            "access",
            "standard",
            "advanced"
        }

        score += len(
            t & adoption_terms
        ) * 5

    # ---------------------------------------------------------------
    # 5. Penalize vocabulary belonging to another question
    # ---------------------------------------------------------------

    negative_matches = len(
        t & profile["negative"]
    )

    score -= negative_matches * 3

    # ---------------------------------------------------------------
    # 6. Interviewer questions are not evidence
    # ---------------------------------------------------------------

    if is_interviewer_question(text):
        score -= 60

    # ---------------------------------------------------------------
    # 7. Prefer substantive answer chunks
    # ---------------------------------------------------------------

    word_count = len(t)

    if word_count >= 15:
        score += 4

    if word_count >= 30:
        score += 3

    return score


def retrieve(query: str, top_k: int = 6):
    """
    Retrieve evidence while preserving cross-market coverage.

    Strategy:
    1. Score every transcript chunk against the question.
    2. Group results by market.
    3. Select the strongest relevant result from each market.
    4. Fill remaining slots with additional high-scoring evidence.
    5. Allow at most two evidence items per market.
    """

    chunks = all_chunks()

    if not chunks:
        return []

    scored = []

    for chunk in chunks:

        score = score_chunk(
            query,
            chunk
        )

        if score > 0:
            scored.append(
                (score, chunk)
            )

    if not scored:
        return []

    # Highest relevance first.
    scored.sort(
        key=lambda item: item[0],
        reverse=True
    )

    # ---------------------------------------------------------------
    # Group candidates by market.
    # ---------------------------------------------------------------

    candidates_by_market = {}

    for score, chunk in scored:

        market = chunk.get(
            "market",
            "Unknown"
        )

        if market not in candidates_by_market:
            candidates_by_market[market] = []

        candidates_by_market[market].append(
            (score, chunk)
        )

    # Keep strongest candidates per market.
    for market in candidates_by_market:

        candidates_by_market[market] = (
            candidates_by_market[market][:4]
        )

    # ---------------------------------------------------------------
    # First pass:
    # strongest result from every market.
    # ---------------------------------------------------------------

    selected = []
    selected_ids = set()
    market_counts = {}

    for market, candidates in candidates_by_market.items():

        if not candidates:
            continue

        best_score, best_chunk = candidates[0]

        chunk_id = best_chunk.get("id")

        if chunk_id in selected_ids:
            continue

        selected.append(best_chunk)
        selected_ids.add(chunk_id)

        market_counts[market] = 1

    # ---------------------------------------------------------------
    # Second pass:
    # additional supporting evidence.
    # Maximum two pieces per market.
    # ---------------------------------------------------------------

    for score, chunk in scored:

        if len(selected) >= top_k:
            break

        chunk_id = chunk.get("id")

        if chunk_id in selected_ids:
            continue

        market = chunk.get(
            "market",
            "Unknown"
        )

        if market_counts.get(market, 0) >= 2:
            continue

        selected.append(chunk)
        selected_ids.add(chunk_id)

        market_counts[market] = (
            market_counts.get(market, 0) + 1
        )

    return selected[:top_k]