import psycopg
from ..models import ConexionBase



def obtener_configuracion_activa():
    """
    Obtiene las credenciales de la única conexión activa.
    No crea ni duplica registros de conexiones.
    """

    conexiones = list(
        ConexionBase.objects.filter(status=True)[:2]
    )

    if not conexiones:
        raise ValueError("No hay una conexión activa configurada.")

    if len(conexiones) > 1:
        raise ValueError(
            "Hay varias conexiones activas. Debe existir solo una."
        )

    conexion = conexiones[0]

    return {
        "host": conexion.host,
        "port": conexion.port,
        "dbname": conexion.dbname,
        "user": conexion.user,
        "password": conexion.password,
        "connect_timeout": 10,
    }


def conectar_base_activa():
    """
    Abre una conexión a la base de datos seleccionada.
    El código que llama esta función debe cerrar la conexión.
    """

    configuracion = obtener_configuracion_activa()

    return psycopg.connect(**configuracion)

