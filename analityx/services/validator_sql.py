import re


def validar_sql(sql):

    sql = sql.strip()

    # solo SELECT
    if not sql.lower().startswith("select"):
        raise Exception("Solo se permiten consultas SELECT")

    # bloquear peligrosos
    bloqueados = ["delete", "update", "insert", "drop", "alter"]

    for b in bloqueados:
        if b in sql.lower():
            raise Exception("Consulta no permitida")

    # corregir numeros sin comillas
    sql = re.sub(
        r"=\s*(\d+)",
        r"= '\1'",
        sql
    )

    return sql