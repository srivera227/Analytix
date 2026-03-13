from django.db import connection


def obtener_schema():

    sql = """
    SELECT
        table_name,
        column_name,
        data_type
    FROM information_schema.columns
    WHERE table_schema = 'public'
    ORDER BY table_name
    """

    with connection.cursor() as cursor:

        cursor.execute(sql)

        rows = cursor.fetchall()

    schema = {}

    for table, column, dtype in rows:

        schema.setdefault(table, []).append(column)

    texto = ""

    for t, cols in schema.items():

        texto += f"{t}({', '.join(cols)})\n"

    return texto