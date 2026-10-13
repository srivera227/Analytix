import psycopg


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "gt_conduccion",
    "user": "postgres",
    "password": "Zqwert178945.",
}


def obtener_schema():

    query = """
        SELECT
            c.table_name,
            c.column_name,
            c.data_type,

            EXISTS (
                SELECT 1
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                    AND tc.table_name = kcu.table_name
                WHERE tc.constraint_type = 'PRIMARY KEY'
                    AND kcu.table_schema = c.table_schema
                    AND kcu.table_name = c.table_name
                    AND kcu.column_name = c.column_name
            ) AS es_pk,

            EXISTS (
                SELECT 1
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                    AND tc.table_name = kcu.table_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND kcu.table_schema = c.table_schema
                    AND kcu.table_name = c.table_name
                    AND kcu.column_name = c.column_name
            ) AS es_fk

        FROM information_schema.columns c

        WHERE c.table_schema = 'public'

        ORDER BY
            c.table_name,
            c.ordinal_position;
    """

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

    schema = {}

    for table, column, dtype, es_pk, es_fk in rows:

        schema.setdefault(table, []).append({
            "table":table
            #"column": column,
            #"type": dtype,
            #"es_pk": es_pk,
            #"es_fk": es_fk,
        })


    return schema