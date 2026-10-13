
import requests
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

api_key = os.getenv("GEMINI_API_KEY")
URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:8b"



def agent_sql(prompt):
    print("Cargando modelo, esperando respuesta")
    r = requests.post(
        URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        },
        timeout=400,
    )

    r.raise_for_status()

    return r.json()["response"]

def ask_llmGemini(prompt):
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta configurar GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)

    print("Enviando solicitud a Gemini 3.8 Flash...")

    try:
        respuesta = client.interactions.create(
            model="gemini-3.8-flash",
            input=prompt,
        )

        texto = respuesta.output_text

        if not texto:
            raise RuntimeError("Gemini no devolvió texto.")

        return texto.strip()

    except Exception as error:
        print(f"Error al consultar Gemini: {error}")
        raise

