"""
classifier.py
--------------
Capa de lógica IA: toma una descripción de tarea y devuelve un
diccionario JSON con:
  - cuadrante
  - justificacion
  - recomendacion
  - energia
  - bloque_sugerido
"""

import json
from openai import OpenAI
from config import OPENAI_API_KEY

# Cliente OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Prompt definitivo (una sola fuente de verdad)
PROMPT_TEMPLATE = """
    Eres un sistema inteligente de productividad que analiza tareas y las clasifica según la matriz de Eisenhower y el tipo de energía requerida.

    Analiza la siguiente tarea ingresada por el usuario y responde en formato JSON estricto con la siguiente estructura:

    {{
    "cuadrante": "I | II | III | IV",
    "justificacion": "<Explicación clara del porqué se asigna al cuadrante>",
    "recomendacion": "<Consejo práctico sobre cómo actuar con esta tarea>",
    "energia": "Alta concentración | Automática o repetitiva | Creativa o estratégica",
    "bloque_sugerido": "<Ej. Martes en la mañana, Viernes por la tarde, justo después del almuerzo, etc.>"
      "duracion_estimada": <entero en minutos, múltiplo de 15>,
        "subtareas": [
            {{"descripcion": "<texto>", "duracion": <minutos>}},
            …
        ]
    }}

    **Reglas adicionales para *subtareas* (★):**
    1. Solo incluye el campo `subtareas` si `duracion_estimada` > 120 min.
    2. Genera 2-4 subtareas cuya suma ≈ duración total.
    3. **Cada subtarea debe referirse explícitamente a la acción principal descrita en la tarea**
    4. Usa verbos concretos: Analizar, Configurar, Modificar, Probar, Documentar, Desplegar.
    5. Duración de cada subtarea ≤ 60 min y múltiplo de 15 min.
    6. NO incluyas la tarea original en tu respuesta.

    **Definiciones:**
    - Cuadrante I: Urgente + Importante (crisis, entregas inmediatas)
    - Cuadrante II: No urgente + Importante (estrategia, prevención, planeación)
    - Cuadrante III: Urgente + No importante (interrupciones, cosas delegables)
    - Cuadrante IV: No urgente + No importante (distracciones, cosas que se pueden eliminar)

    - Alta concentración: tareas críticas, análisis profundo, decisiones importantes.
    - Automática o repetitiva: correos, tareas administrativas o mecánicas.
    - Creativa o estratégica: innovación, lluvia de ideas, diseño, planeación.
    
    Devuelve además "duracion_estimada": número entero de minutos que tomaría la tarea (usa múltiplos de 15).

    **Tarea a analizar:**
    "{tarea}"
"""

def clasificar_tarea(tarea: str) -> dict:
    """
    Envía la tarea al modelo y devuelve un dict con la clasificación.
    Lanza ValueError si la respuesta no es JSON válido.
    """
    messages = [{
        "role": "user",
        "content": PROMPT_TEMPLATE.format(tarea=tarea)
    }]

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        response_format={"type": "json_object"}
    )

    raw = resp.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Respuesta no es JSON válido: {raw}") from e

def clasificar_varias_tareas(texto_multilinea: str) -> list[dict]:
    """
    Recibe un bloque de texto con varias líneas.
    Devuelve una lista con un dict de clasificación por línea no vacía.
    """
    tareas = [line.strip() for line in texto_multilinea.splitlines() if line.strip()]
    resultados = []
    for t in tareas:
        try:
            resultados.append({"tarea": t, **clasificar_tarea(t)})
        except Exception as e:
            resultados.append({"tarea": t, "error": str(e)})
    return resultados
