from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import auth, users, documents, paraphrase, chat, detect_ai, detect_plagiarism

# Crea las tablas si no existen. Para un proyecto que vaya a crecer mucho,
# en algún momento conviene cambiar esto por migraciones con Alembic.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Plumia API",
    description="Backend de ejemplo para la herramienta de reescritura Plumia.",
    version="0.1.0",
)

# En producción, cambia allow_origins=["*"] por el dominio real de tu frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(paraphrase.router)
app.include_router(chat.router)
app.include_router(detect_ai.router)
app.include_router(detect_plagiarism.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "plumia-api"}
