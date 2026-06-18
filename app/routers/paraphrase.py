from fastapi import APIRouter, Depends, HTTPException

from .. import models, schemas, security, claude_client
from ..config import settings

router = APIRouter(prefix="/paraphrase", tags=["paraphrase"])


def count_words(text: str) -> int:
    text = (text or "").strip()
    return len(text.split()) if text else 0


@router.post("", response_model=schemas.ParaphraseResponse)
def paraphrase_text(
    payload: schemas.ParaphraseRequest,
    current_user: models.User = Depends(security.get_current_user),
):
    word_count = count_words(payload.text)

    if word_count == 0:
        raise HTTPException(status_code=400, detail="El texto está vacío.")

    # Límite real, aplicado en el servidor (a diferencia de la demo en HTML,
    # esto no se puede saltar editando el navegador).
    if current_user.plan != models.PlanType.premium and word_count > settings.free_word_limit:
        raise HTTPException(
            status_code=402,
            detail=(
                f"El plan gratis admite hasta {settings.free_word_limit} palabras por "
                "reescritura. Pásate a Premium para escribir sin límite."
            ),
        )

    try:
        result = claude_client.paraphrase(
            text=payload.text,
            mode=payload.mode,
            custom_instruction=payload.custom_instruction,
            language=payload.language,
        )
    except RuntimeError as e:
        # Falta la API key u otro error de configuración.
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        raise HTTPException(status_code=502, detail="No se pudo generar la reescritura. Inténtalo de nuevo.")

    return schemas.ParaphraseResponse(
        result=result,
        word_count_input=word_count,
        word_count_output=count_words(result),
    )
