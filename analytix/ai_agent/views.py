from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services.bi_agent import ai_agent
from modeler.services.schema_service import obtener_columnas
from bi_agent.services.schema_analyzer import analizar_tablas_seleccionadas
from bi_agent.services.dashboard_service import obtener_o_generar_dashboard_general
from bi_agent.services.dashboard_data_service import controlador_datos
from bi_agent.models import Dashboard, DashboardWidget, DashboardWidgetData
from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch



def vistaHome(request):
    if request.method == "GET":
        return render(request,"account/home.html")
    


def dashboard_renderer(request, dashboard_id):

    if request.method != "GET":
        return render(
                request,
                "account/dashboard.html")
    
    print(f"request: {request}")

    dashboard = get_object_or_404(
        Dashboard,
        id=dashboard_id,
        status=Dashboard.Status.READY
    )

    

    widgets = (
        DashboardWidget.objects
        .filter(dashboard=dashboard, enabled=True)
        .select_related("data")
        .order_by("position")
    )

    widgets_data = []

    for widget in widgets:

        try:
            registro = widget.data
            datos = registro.data
            columnas = registro.columns
            ultima_actualizacion = registro.last_refreshed_at.isoformat() if registro.last_refreshed_at else None
            error = registro.last_error

        except DashboardWidgetData.DoesNotExist:
            datos = []
            columnas = []
            ultima_actualizacion = None
            error = "El widget todavía no tiene datos."

        widgets_data.append({
            "id": str(widget.id),
            "key": widget.key,
            "title": widget.title,
            "description": widget.description,
            "widget_type": widget.widget_type,
            "config": widget.config,
            "position": widget.position,
            "data": datos,
            "columns": columnas,
            "last_refreshed_at": ultima_actualizacion,
            "error": error
        })

    context = {
        "dashboard": dashboard,
        "widgets": widgets_data,
        "total_widgets": len(widgets_data)
    }

    return render(
        request,
        "account/dashboard.html",
        context
    )



@api_view(["POST"])
def ai_query(request):

    pregunta = request.data["pregunta"]
    print(f"Pregunta: {pregunta}")

    schema = request.data.get("schema")
    tablasUsadas = request.data.get("tablasUsadas")
    columnastablas = dict(obtener_columnas(tablasUsadas))

    r = ai_agent(pregunta,schema,tablasUsadas,columnastablas)

    return Response({
        "respuesta": r
    })



@api_view(["GET"])
def bulid_dashborad(request):
    """
    Analiza las tablas seleccionadas, genera el dashboard,
    ejecuta las consultas SQL de sus widgets y almacena
    los resultados para su posterior visualización.
    """

    # 1. Obtener y validar las tablas seleccionadas
    tablas_param = request.GET.get("tablas", "")

    nombres_tablas = list(dict.fromkeys(
        tabla.strip()
        for tabla in tablas_param.split(",")
        if tabla.strip()
    ))

    if not nombres_tablas:
        return Response(
            {
                "success": False,
                "error": "Debes seleccionar al menos una tabla."
            },
            status=400
        )

    try:
        print("Tablas recibidas:", nombres_tablas)

        # 2. Analizar el esquema completo
        print("Analizando esquema...")

        resultado = analizar_tablas_seleccionadas(nombres_tablas)

        if not isinstance(resultado, dict):
            raise ValueError("El analizador devolvió una estructura inválida.")

        if resultado.get("error"):
            return Response(
                {
                    "success": False,
                    "error": resultado["error"]
                },
                status=400
            )

        if not resultado.get("tablas"):
            return Response(
                {
                    "success": False,
                    "error": "No se encontraron tablas para analizar."
                },
                status=400
            )

        # 3. Obtener o generar el dashboard
        print("Obteniendo o generando dashboard...")

        dashboard, creado = obtener_o_generar_dashboard_general(
            resultado
        )

        print(
            f"Dashboard ID: {dashboard.id} | "
            f"Creado: {creado}"
        )

        # 4. Ejecutar SQL de cada widget y almacenar resultados
        print("Procesando datos de los widgets...")

        procesamiento = controlador_datos(dashboard.id)

        print("Resultado del procesamiento:", procesamiento)

        # 5. Construir respuesta
        if not procesamiento["success"]:
            return Response(
                {
                    "success": False,
                    "dashboard_id": str(dashboard.id),
                    "dashboard_name": dashboard.name,
                    "dashboard_status": procesamiento["status"],
                    "dashboard_created": creado,
                    "widgets": {
                        "total": procesamiento["total_widgets"],
                        "exitosos": procesamiento["widgets_exitosos"],
                        "fallidos": procesamiento["widgets_fallidos"],
                    },
                    "resultados": procesamiento["resultados"],
                    "message": "El dashboard fue creado, pero algunos widgets no pudieron procesarse."
                },
                status=500
            )

        return Response(
            {
                "success": True,
                "dashboard_id": str(dashboard.id),
                "dashboard_name": dashboard.name,
                "dashboard_status": dashboard.status,
                "dashboard_created": creado,
                "widgets": {
                    "total": procesamiento["total_widgets"],
                    "exitosos": procesamiento["widgets_exitosos"],
                    "fallidos": procesamiento["widgets_fallidos"],
                },
                "message": "Dashboard generado correctamente."
            },
            status=200
        )

    except Exception as e:

        print(f"Error al generar dashboard: {e}")

        return Response(
            {
                "success": False,
                "error": str(e),
                "message": "No fue posible generar el dashboard."
            },
            status=500
        )







