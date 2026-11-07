
import os
import anthropic

api_key = os.getenv("ANTHROPIC_API_KEY")
workspace_id = os.getenv("ANTHROPIC_WORKSPACE_ID")

if not api_key:
    raise RuntimeError("Falta ANTHROPIC_API_KEY en el entorno.")

headers = {}

if workspace_id:
    headers["anthropic-workspace-id"] = workspace_id

client = anthropic.Anthropic(
    api_key=api_key,
    default_headers=headers,
)

MODEL = os.getenv(
    "ANTHROPIC_MODEL",
    "claude-haiku-5-5",
)



def consultar_claude(prompt, max_tokens: int = 8192) -> str:

    if not prompt or not prompt.strip():
        raise ValueError("El prompt no puede estar vacío.")

    print(f"Usando Claude... max_tokens={max_tokens}")

    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    if response.stop_reason == "max_tokens":
        raise RuntimeError(
            f"Claude alcanzó el límite de {max_tokens} tokens "
            "y truncó la respuesta. Reduce el tamaño del prompt "
            "o divide la generación en varias solicitudes."
        )

    respuesta = "\n".join(
        block.text
        for block in response.content
        if block.type == "text"
    ).strip()

    if not respuesta:
        raise RuntimeError(
            f"Claude no devolvió contenido de texto. "
            f"Motivo de finalización: {response.stop_reason}"
        )

    print(f"Claude finalizó. Motivo: {response.stop_reason}")

    return respuesta

