from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .. import models, security, claude_client

router = APIRouter(prefix="/detect-ai", tags=["detect-ai"])


class DetectRequest(BaseModel):
    text: str


class DetectResponse(BaseModel):
    verdict: str
    confidence: int
    reason: str


@router.post("", response_model=DetectResponse)
def detect_ai_endpoint(
    payload: DetectRequest,
    current_user: models.User = Depends(security.get_current_user),
):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="El texto está vacío.")
    try:
        result = claude_client.detect_ai(payload.text)
        return DetectResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        raise HTTPException(status_code=502, detail="No se pudo analizar el texto.")
