from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..database import get_db

router = APIRouter(prefix="/documents", tags=["documents"])


def _get_owned_document(doc_id: int, current_user: models.User, db: Session) -> models.Document:
    doc = (
        db.query(models.Document)
        .filter(models.Document.id == doc_id, models.Document.owner_id == current_user.id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Ficha no encontrada.")
    return doc


@router.get("", response_model=List[schemas.DocumentOut])
def list_documents(
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Document)
        .filter(models.Document.owner_id == current_user.id)
        .order_by(models.Document.updated_at.desc())
        .all()
    )


@router.post("", response_model=schemas.DocumentOut, status_code=status.HTTP_201_CREATED)
def create_document(
    payload: schemas.DocumentCreate,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db),
):
    doc = models.Document(owner_id=current_user.id, title=payload.title, content=payload.content)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{doc_id}", response_model=schemas.DocumentOut)
def get_document(
    doc_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db),
):
    return _get_owned_document(doc_id, current_user, db)


@router.put("/{doc_id}", response_model=schemas.DocumentOut)
def update_document(
    doc_id: int,
    payload: schemas.DocumentUpdate,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db),
):
    doc = _get_owned_document(doc_id, current_user, db)
    if payload.title is not None:
        doc.title = payload.title
    if payload.content is not None:
        doc.content = payload.content
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    doc_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db),
):
    doc = _get_owned_document(doc_id, current_user, db)
    db.delete(doc)
    db.commit()
    return None
