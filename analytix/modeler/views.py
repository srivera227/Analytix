from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .services.database_connection import probar_conexion
from .models import ConexionBase
from .services.database_service import conectar_base_activa
from .services.schema_service import obtener_tablas
# Create your views here.

@api_view(["POST"])
def conectar_bd(request):

    config = {
        "host": request.data.get("host"),
        "port": request.data.get("port", 5432),
        "database": request.data.get("database"),
        "user": request.data.get("user"),
        "password": request.data.get("password"),
    }

    campos_obligatorios = [
        "host",
        "database",
        "user",
        "password",
    ]

    print(config)

    for campo in campos_obligatorios:
        if not config[campo]:
            return Response(
                {
                    "ok": False,
                    "mensaje": f"El campo '{campo}' es obligatorio."
                },
                status=400
            )
        

    resultado = probar_conexion(config)

    if not resultado["ok"]:
        return Response(
            resultado,
            status=400
        )

    return Response(resultado)

@api_view(["GET"])
def listarConexiones(request):

    conexiones = ConexionBase.objects.all()

    resultado = []

    for c in conexiones:
        resultado.append({
            "id": c.id,
            "nombre": c.dbname,
            "motor": getattr(c, "motor", "PostgreSQL"),
            "host": c.host,
            "puerto": c.port,
            "estado": c.status,
        })
   
    return Response({
        "conexiones": resultado,
        "conexion_activa_id": None,
    })


@api_view(["GET"])
def gestionarConexion(request):
    conexionId= request.GET.get("id")
    accion=  request.GET.get("accion")

    if accion == "activar":
        try:
            conexion = ConexionBase.objects.get(id=conexionId)

            conexion.status = True
            conexion.save(update_fields=["status"])
            schema = list(obtener_tablas())
            return Response({
                "ok": True,
                "mensaje": "Conexión activada correctamente.",
                "schema":schema
        
            })

        except ConexionBase.DoesNotExist:
            return Response({
                "ok": False,
                "mensaje": "La conexión no existe."
            }, status=404)
        
    elif accion == "desactivar":
        try:
            conexion = ConexionBase.objects.get(id=conexionId)
            conexion.status = False
            conexion.save(update_fields=["status"])
            
            return Response({
                "ok": True,
                "mensaje": "Conexión desactivada correctamente.",
               
                })
        
        except ConexionBase.DoesNotExist:
                return Response({
                        "ok": False,
                        "mensaje": "La conexión no existe."
                    }, status=404)

@api_view(["POST"])
def desactivarConexion(request, pk):
    try:
        conexion = ConexionBase.objects.get(pk=pk)

        conexion.status = False
        conexion.save(update_fields=["status"])

        return Response({
            "ok": True,
            "mensaje": "Conexión desactivada correctamente."
        })

    except ConexionBase.DoesNotExist:
        return Response({
            "ok": False,
            "mensaje": "La conexión no existe."
        }, status=404)