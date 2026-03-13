import requests

URL = "http://localhost:11434/api/generate"


def ask_llm(prompt):     

    r = requests.post(
        URL,
        json={
            "model": "mistral", #mistral
            "prompt": prompt,
            "stream": False,
        },
    )

    return r.json()["response"]