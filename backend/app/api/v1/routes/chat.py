from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.core.twin import DigitalTwin


router = APIRouter(prefix="/chat", tags=["Cognition"])

# 🔥 Singleton brain
twin = DigitalTwin()

class ChatRequest(BaseModel):
    query: str
    agent: str = "AssistantBot"

class ChatResponse(BaseModel):
    status: str
    operation: str
    memory_type: str
    answer: str
    response: str
    timestamp_id: str
    emotions: dict | None = None

@router.post("/query", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = twin.process_query(req.query, req.agent)

    try:
        emotions = twin.get_emotion_dict(req.query)
        result["emotions"] = dict(
            sorted(emotions.items(), key=lambda x: x[1], reverse=True)
        )
    except Exception:
        result["emotions"] = {}

    return result
