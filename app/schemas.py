from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- Usuarios ----------

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    plan: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Fichas / documentos ----------

class DocumentCreate(BaseModel):
    title: Optional[str] = "Sin título"
    content: Optional[str] = ""


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime


# ---------- Parafraseo ----------

class ParaphraseRequest(BaseModel):
    text: str
    mode: str = "estandar"
    custom_instruction: Optional[str] = None
    language: str = "es"


class ParaphraseResponse(BaseModel):
    result: str
    word_count_input: int
    word_count_output: int
