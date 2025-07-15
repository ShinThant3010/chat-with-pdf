# app/main.py

import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from app.pdf_ingest import PDFIngestor
from app.agents import router_agent, router_agent_with_history

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# Initialize and ingest on startup
pdf_ingestor = PDFIngestor()
pdf_ingestor.ingest()

# Global in-memory session store (for demo)
session_store = {}

class QuestionRequest(BaseModel):
    session_id: Optional[str] = None
    question: str

class ClearMemoryRequest(BaseModel):
    session_id: str

@app.post("/ask")
def ask_question(req: QuestionRequest):
    session_id = req.session_id if req.session_id else str(uuid.uuid4())
    # Load previous chat history
    history = session_store.get(session_id, [])
    
    # Optionally, add previous Q&A as extra context (see below)
    # answer, agent = router_agent(pdf_ingestor, req.question)
    answer, agent = router_agent_with_history(pdf_ingestor, req.question, history)
    
    # Add new turn to session history
    history.append({"question": req.question, "answer": answer, "agent": agent})
    session_store[session_id] = history
    return {
        "answer": answer,
        "agent": agent,
        "session_id": session_id,
        "history": history
    }

# @app.post("/ask")
# def ask_question(req: QuestionRequest):
#     answer = router_agent(pdf_ingestor, req.question)
#     # Add to session memory
#     if req.session_id not in session_store:
#         session_store[req.session_id] = []
#     session_store[req.session_id].append({"question": req.question, "answer": answer["answer"], "agent": answer["agent"]})
#     return {
#         "answer": answer["answer"],
#         "agent": answer["agent"],
#         "session_id": req.session_id,
#         "history": session_store[req.session_id]  # (optional, returns history)
#     }

@app.post("/clear")
def clear_memory(req: ClearMemoryRequest):
    # Remove session from store
    if req.session_id in session_store:
        del session_store[req.session_id]
        return {"message": f"Session {req.session_id} memory cleared."}
    else:
        return {"message": f"Session {req.session_id} did not exist or was already cleared."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
