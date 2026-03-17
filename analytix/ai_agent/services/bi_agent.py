from .llm_service import ask_llm
from .db_service import ejecutar_sql
from .validator_sql import validar_sql
from .sql_service import generar_sql


def bi_agent(pregunta):

    # 1 generar sql
    sql = generar_sql(pregunta)

    sql = validar_sql(sql)

    # 2 ejecutar
    resultado = ejecutar_sql(sql)

    # 3 responder con datos (NO explicar)
    respuesta = ask_llm(
        f"""
            Responde mostrando los datos en texto claro.

            No expliques.
            No describas.
            Solo muestra los datos.

            Datos:
            {resultado}
            """
    )

    return respuesta