from typing import Optional

from google import genai

from .config import settings

_client = None

MODE_INSTRUCTIONS = {
    "estandar": "Reescribe el texto manteniendo su significado original, con un tono neutro y natural.",
    "humanizar": "Reescribe el texto para que suene completamente natural y humano, evitando frases hechas o patrones típicos de un texto generado por IA.",
    "formal": "Reescribe el texto en un tono formal y profesional, cuidando el registro.",
    "academico": "Reescribe el texto con un registro académico, vocabulario preciso y estructura propia de un texto académico.",
    "simple": "Reescribe el texto utilizando un lenguaje más simple y claro, con frases cortas y vocabulario accesible.",
    "creativo": "Reescribe el texto de forma creativa y expresiva, variando la estructura de las frases.",
    "ampliar": "Reescribe el texto añadiendo más detalle y desarrollo de las ideas, ampliando claramente su extensión.",
    "acortar": "Reescribe el texto de forma mucho más breve y concisa, manteniendo solo las ideas esenciales.",
}


def get_client():
    global _client
    if _client is None:
        if not settings.gemini_api_key:
            raise RuntimeError(
                "Falta GEMINI_API_KEY en el archivo .env. "
                "Consíguela gratis en https://aistudio.google.com"
            )
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def paraphrase(text: str, mode: str, custom_instruction: Optional[str], language: str) -> str:
    if mode == "personalizado" and custom_instruction and custom_instruction.strip():
        instruction = custom_instruction.strip()
    else:
        instruction = MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["estandar"])

    lang_line = "Responde en inglés." if language == "en" else "Responde en español."

    prompt = (
        "Eres una herramienta de reescritura de texto. " + instruction +
        " Responde ÚNICAMENTE con el texto reescrito, sin comentarios, explicaciones ni comillas adicionales. " +
        lang_line + "\n\nTexto a reescribir:\n" + text
    )

    client = get_client()
    response = client.models.generate_content(model="gemini-flash-lite-latest", contents=prompt)
    return response.text.strip()
