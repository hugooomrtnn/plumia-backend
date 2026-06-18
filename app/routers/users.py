from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..database import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserOut)
def read_me(current_user: models.User = Depends(security.get_current_user)):
    return current_user


@router.post("/me/upgrade", response_model=schemas.UserOut)
def upgrade_to_premium(
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Marca al usuario como premium.

    Esto es un sustituto temporal de un cobro real. Cuando conectes Stripe,
    este endpoint se sustituye por el webhook que Stripe llama cuando un
    pago se confirma.
    """
    current_user.plan = models.PlanType.premium
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/downgrade", response_model=schemas.UserOut)
def downgrade_to_free(
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db),
):
    """Solo para pruebas: vuelve a poner al usuario en el plan gratis."""
    current_user.plan = models.PlanType.free
    db.commit()
    db.refresh(current_user)
    return current_user
