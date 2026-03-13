from django.db import connection


def ejecutar_sql(sql):

    with connection.cursor() as cursor:

        cursor.execute(sql)

        cols = [c[0] for c in cursor.description]

        data = [
            dict(zip(cols, row))
            for row in cursor.fetchall()
        ]

    return data