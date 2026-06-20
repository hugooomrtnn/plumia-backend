from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List

from .. import models, security, claude_client

router = APIRouter(prefix="/chat", tags=["chat"])


class HistoryMessage(BaseModel):
    role: str
    text: str


class ChatRequest(BaseModel):
    message: str
    history: List[HistoryMessage] = []


class ChatResponse(BaseModel):
    response: str


@router.post("", response_model=ChatResponse)
def chat_endpoint(
    payload: ChatRequest,
    current_user: models.User = Depends(security.get_current_user),
):
    try:
        history = [{"role": m.role, "text": m.text} for m in payload.history]
        result = claude_client.chat(payload.message, history)
        return ChatResponse(response=result)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        raise HTTPException(status_code=502, detail="No se pudo generar una respuesta. Inténtalo de nuevo.")
