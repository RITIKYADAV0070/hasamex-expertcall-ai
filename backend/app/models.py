
from pydantic import BaseModel
from typing import List

class Evidence(BaseModel):
    transcript_id: str
    source: str
    expert: str
    market: str
    timestamp: str
    quote: str

class AnswerRequest(BaseModel):
    question_id: int

class AskRequest(BaseModel):
    question: str

class GroundedAnswer(BaseModel):
    answer: str
    evidence: List[Evidence]
