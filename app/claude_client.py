from typing import Optional

from google import genai

from .config import settings

_client = None

MODE_INSTRUCTIONS = {
    "estandar": (
        "Reescribe el siguiente texto de forma que parezca escrito por un humano real. "
        "Varía la longitud de las frases: mezcla frases cortas con otras más largas. "
        "Usa vocabulario variado pero natural, sin palabras rebuscadas. "
        "Evita estructuras repetitivas, transiciones genéricas como 'En conclusión', 'Es importante destacar', 'Cabe mencionar' o 'En el contexto de'. "
        "El resultado debe ser fluido, directo y con la imperfección natural del lenguaje humano. "
        "Mantén el significado original."
    ),
    "humanizar": (
        "Reescribe este texto para que supere cualquier detector de IA universitario o profesional. "
        "Aplica estas técnicas: "
        "1) Varía drásticamente la longitud de las frases (algunas muy cortas, de 3-5 palabras; otras más largas). "
        "2) Usa expresiones coloquiales o giros propios del español hablado cuando encaje. "
        "3) Elimina por completo frases hechas típicas de IA: 'Es fundamental destacar', 'En el marco de', 'Cabe señalar', 'En conclusión', 'En resumen', 'Es importante mencionar'. "
        "4) Rompe el ritmo uniforme: usa puntos y seguido frecuentes, alguna pregunta retórica, o una frase muy directa. "
        "5) Introduce ligeras variaciones de perspectiva o énfasis que un humano añadiría naturalmente. "
        "El resultado debe ser completamente indetectable como texto de IA."
    ),
    "formal": (
        "Reescribe el texto en un tono formal y profesional. "
        "Usa un registro cuidado pero sin caer en frases genéricas de IA. "
        "Varía la estructura de las oraciones y mantén un estilo propio y coherente."
    ),
    "academico": (
        "Reescribe el texto con registro académico: vocabulario preciso, argumentación clara y estructura formal. "
        "Evita clichés de escritura automática. Usa conectores variados y apropiados para el género académico. "
        "El texto debe sonar como escrito por un estudiante o investigador humano experto."
    ),
    "simple": (
        "Reescribe el texto con lenguaje muy simple y directo. "
        "Frases cortas. Palabras de uso común. Sin tecnicismos ni rodeos. "
        "Como si se lo explicaras a alguien que no conoce el tema."
    ),
    "creativo": (
        "Reescribe el texto de forma creativa y expresiva. "
        "Experimenta con la estructura: cambia el orden de las ideas, usa metáforas si encajan, varía el ritmo. "
        "El resultado debe ser memorable y con personalidad propia."
    ),
    "ampliar": (
        "Reescribe el texto desarrollando más cada idea: añade ejemplos, matices o explicaciones adicionales. "
        "Amplía claramente la extensión pero mantén la coherencia. "
        "No rellenes con frases vacías; cada añadido debe aportar valor real."
    ),
    "acortar": (
        "Reescribe el texto de forma muy concisa, conservando solo las ideas esenciales. "
        "Elimina repeticiones, adjetivos innecesarios y rodeos. "
        "El resultado debe ser directo y sustancioso."
    ),
    "corregir": (
        "Corrige todos los errores ortográficos, gramaticales y de puntuación del siguiente texto. "
        "Mantén el estilo, estructura y significado original tal cual. "
        "Solo corrige los errores, no reescribas ni parafrasees."
    ),
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
        "Eres un detector de texto generado por IA de nivel universitario, equivalente a GPTZero o Turnitin AI Detection. "
        "Analiza el siguiente texto con criterio estricto y busca estos indicadores de texto generado por IA:\n"
        "INDICADORES DE IA: frases de longitud uniforme y ritmo constante, uso de transiciones genéricas "
        "('En conclusión', 'Es importante destacar', 'Cabe mencionar', 'En el marco de', 'Es fundamental', "
        "'En el contexto de', 'Cabe señalar'), vocabulario excesivamente formal y sin variación de registro, "
        "ausencia de anécdotas o experiencias personales, estructura perfectamente organizada sin digresiones, "
        "falta de opiniones directas o emociones, redundancias explicativas, párrafos de extensión similar.\n"
        "INDICADORES HUMANOS: variación notable en la longitud de frases, expresiones coloquiales o informales, "
        "errores menores o correcciones, digresiones o ideas no perfectamente hiladas, voz personal y opiniones "
        "directas, vocabulario desigual (mezcla de registros), estructura irregular.\n"
        "Sé estricto: si el texto tiene ritmo uniforme y transiciones típicas de IA, aunque esté 'humanizado', "
        "debe recibir una puntuación alta de IA. Solo texto con características humanas claras merece veredicto 'Humano'.\n"
        "Responde ÚNICAMENTE con un objeto JSON con esta estructura exacta, sin texto adicional:\n"
        "{\"verdict\": \"IA\", \"confidence\": 87, \"reason\": \"El texto presenta...\"}\n"
        "El campo 'verdict' debe ser exactamente 'Humano', 'IA' o 'Mixto'. "
        "'confidence' es un número del 0 al 100 (qué seguro estás del veredicto). "
        "'reason' es una explicación breve en español de los indicadores encontrados.\n\n"
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
        "Eres una herramienta de reescritura de texto experta en producir texto que suene genuinamente humano. "
        + instruction +
        " Responde ÚNICAMENTE con el texto reescrito, sin comentarios, introducciones, explicaciones ni comillas adicionales. "
        "No escribas frases como 'Aquí tienes el texto reescrito' ni similares. Solo el texto. "
        + lang_line + "\n\nTexto a reescribir:\n" + text
    )

    client = get_client()
    response = client.models.generate_content(model="gemini-flash-lite-latest", contents=prompt)
    return response.text.strip()
