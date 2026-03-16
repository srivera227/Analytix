from services.llm_service import ask_llm
from services.schema_service import obtener_schema


def generar_sql(pregunta):

    schema = obtener_schema()

    prompt = f"""
        Eres un asistente que genera SQL seguros y experto en PostgreSQL.
        
        Reglas estrictas:
        1. Solo usar SELECT
        2. No usar INSERT
        3. No usar UPDATE
        4. No usar DELETE
        5. No usar DROP
        6. No usar ALTER
        7. NO usar CREATE
        8. No usar TRUNCATE
        9. No usar WIRTE EXPLANATIONS
        10. Retornar solo SQL

        Tablas disponibles:
        {schema}

        Convierte la pregunta en SQL.

        Pregunta:
        {pregunta}

        Solo responde SQL.
        """

    sql = ask_llm(prompt)
    return sql