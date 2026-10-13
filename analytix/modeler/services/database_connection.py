import psycopg
from ..models import ConexionBase

def probar_conexion(config):
    try:
        print("Intentando conectar...")
        with psycopg.connect(
            host=config["host"],
            port=config["port"],
            dbname=config["database"],
            user=config["user"],
            password=config["password"],
            connect_timeout=10,
        ):
            
            conexion = ConexionBase.objects.create(
                host=config["host"],
                port=int(config["port"]),
                dbname=config["database"],
                user=config["user"],
                password=config["password"],
            )

            return {
                "ok": True,
                "mensaje": "Conexión exitosa",
                "name_conexion": conexion.dbname,
            }

    except psycopg.OperationalError as e:
        return {
            "ok": False,
            "mensaje": str(e)
        }

    except Exception as e:
        return {
            "ok": False,
            "mensaje": str(e)
        }