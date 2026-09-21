
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .store import guide_questions, SOURCES
from .analysis import guide_answer, themes, ask
from .models import AnswerRequest, AskRequest

app = FastAPI(title="Hasamex ExpertCall AI", version="2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/health")
def health():
    return {"status":"ok","version":"2.0"}

@app.get("/api/transcripts")
def transcripts():
    return [{"id":x[0],"source":x[1],"market":x[2],"role":x[3]} for x in SOURCES]

@app.get("/api/guide/questions")
def questions():
    return guide_questions()

@app.post("/api/guide/answer")
def answer(req: AnswerRequest):
    return guide_answer(req.question_id)

@app.post("/api/themes")
def theme_analysis():
    return themes()

@app.post("/api/ask")
def ask_api(req: AskRequest):
    return ask(req.question)
