
from modeler.services.database_service import conectar_base_activa


def ejecutar_sql(sql):
    """
    Ejecuta una consulta SQL exclusivamente de lectura
    en la conexión seleccionada desde el modeler.
    """
    print(f"Ejecutando  la query...")
    sql_limpio = sql.strip().rstrip(";")

    if not sql_limpio:
        raise ValueError("La consulta SQL está vacía.")

    # Validación inicial: solo permitir SELECT o WITH.
    sql_inicio = sql_limpio.lstrip().upper()

    if not (
        sql_inicio.startswith("SELECT ")
        or sql_inicio.startswith("SELECT\n")
        or sql_inicio.startswith("WITH ")
        or sql_inicio.startswith("WITH\n")
    ):
        raise ValueError("Solo se permiten consultas SELECT.")
    print(f"Sql a usar: {sql_limpio}")
    # Evitar múltiples sentencias SQL.
    if ";" in sql_limpio:
        raise ValueError("Solo se permite una sentencia SQL por consulta.")

    with conectar_base_activa() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(sql_limpio)

            columnas = [columna.name for columna in cursor.description]
            filas = cursor.fetchall()

            return {
                "columnas": columnas,
                "filas": filas,
                "total": len(filas),
            }

