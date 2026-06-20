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
    "corregir": "Corrige todos los errores ortográficos, gramaticales y de puntuación del siguiente texto. Mantén el estilo, estructura y significado original tal cual. Solo corrige los errores, no reescribas ni parafrasees.",
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


def detect_plagiarism(text: str) -> dict:
    import json, re
    prompt = (
        "Actúa como una herramienta de análisis de originalidad de texto. "
        "Analiza el siguiente texto y evalúa su originalidad basándote en: "
        "uso de frases genéricas o clichés, consistencia de estilo y voz narrativa, "
        "y patrones que puedan indicar texto copiado o no original. "
        "Responde ÚNICAMENTE con un objeto JSON con esta estructura exacta, sin texto adicional:\n"
        "{\"risk\": \"Bajo\", \"originality\": 92, \"summary\": \"El texto parece original...\", \"flags\": [\"frase sospechosa 1\"]}\n"
        "'risk' debe ser exactamente 'Bajo', 'Medio' o 'Alto'. "
        "'originality' es el porcentaje estimado de originalidad (0-100). "
        "'summary' es un párrafo breve en español. "
        "'flags' es una lista de hasta 3 frases sospechosas (puede ser lista vacía []).\n\n"
        "Texto a analizar:\n" + text
    )
    client = get_client()
    response = client.models.generate_content(model="gemini-flash-lite-latest", contents=prompt)
    match = re.search(r'\{.*?\}', response.text.strip(), re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return {"risk": "Desconocido", "originality": 0, "summary": "No se pudo analizar el texto.", "flags": []}


def detect_ai(text: str) -> dict:
    import json, re
    prompt = (
        "Analiza el siguiente texto y determina si fue escrito por un humano o generado por IA. "
        "Responde ÚNICAMENTE con un objeto JSON con esta estructura exacta, sin texto adicional:\n"
        "{\"verdict\": \"Humano\", \"confidence\": 85, \"reason\": \"El texto presenta...\"}\n"
        "El campo 'verdict' debe ser exactamente 'Humano', 'IA' o 'Mixto'. "
        "'confidence' es un número del 0 al 100. 'reason' es una frase breve en español.\n\n"
        "Texto a analizar:\n" + text
    )
    client = get_client()
    response = client.models.generate_content(model="gemini-flash-lite-latest", contents=prompt)
    match = re.search(r'\{[^{}]*\}', response.text.strip(), re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return {"verdict": "Desconocido", "confidence": 0, "reason": "No se pudo analizar el texto."}


def chat(message: str, history: list) -> str:
    contents = []
    for msg in history:
        contents.append({"role": msg["role"], "parts": [{"text": msg["text"]}]})
    contents.append({"role": "user", "parts": [{"text": message}]})
    client = get_client()
    response = client.models.generate_content(model="gemini-flash-lite-latest", contents=contents)
    return response.text.strip()


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
