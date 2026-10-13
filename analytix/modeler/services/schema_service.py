
# modeler/services/schema_service.py

from .database_service import conectar_base_activa

TABLAS_EXCLUIDAS = {
    "django_migrations",
    "django_content_type",
    "django_session",
    "django_admin_log",
    "auth_permission",
    "auth_group",
    "auth_group_permissions",
    "auth_user",
    "auth_user_groups",
    "auth_user_user_permissions",
}

def obtener_tablas():
    """
    Obtiene las tablas de negocio del esquema public,
    excluyendo las tablas internas de Django y autenticación.
    """

    consulta = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """

    with conectar_base_activa() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta)
            resultados = cursor.fetchall()

    tablas = [
        fila[0]
        for fila in resultados
        if fila[0] not in TABLAS_EXCLUIDAS
        and not fila[0].startswith(("django_", "auth_", "admin_"))
    ]

    return tablas



def obtener_columnas(tablas=None):
    """
    Obtiene las columnas de una o varias tablas del esquema public.

    Args:
        tablas (str | list | None):
            - str: nombre de una tabla.
            - list: lista de tablas.
            - None: todas las tablas de negocio.

    Returns:
        dict: Diccionario con las tablas y sus columnas.
    """

    if isinstance(tablas, str):
        tablas = [tablas]

    # Si no se especifican tablas, obtener las tablas de negocio.
    if tablas is None:
        tablas = obtener_tablas()

    if not tablas:
        return {}

    consulta = """
        SELECT
            table_name,
            column_name,
            data_type,
            is_nullable,
            ordinal_position
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = ANY(%s)
        ORDER BY table_name, ordinal_position;
    """

    resultado = {}

    with conectar_base_activa() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (tablas,))
            filas = cursor.fetchall()

    for tabla, columna, tipo, nullable, posicion in filas:
        resultado.setdefault(tabla, []).append({
            "nombre": columna,
            "tipo": tipo,
            "nullable": nullable == "YES",
            "posicion": posicion
        })

    return resultado