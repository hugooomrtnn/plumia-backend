from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List

from .. import models, security, claude_client

router = APIRouter(prefix="/detect-plagiarism", tags=["detect-plagiarism"])


class DetectPlagiarismRequest(BaseModel):
    text: str


class DetectPlagiarismResponse(BaseModel):
    risk: str
    originality: int
    summary: str
    flags: List[str] = []


@router.post("", response_model=DetectPlagiarismResponse)
def detect_plagiarism_endpoint(
    payload: DetectPlagiarismRequest,
    current_user: models.User = Depends(security.get_current_user),
):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="El texto está vacío.")
    try:
        result = claude_client.detect_plagiarism(payload.text)
        return DetectPlagiarismResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        raise HTTPException(status_code=502, detail="No se pudo analizar el texto.")
