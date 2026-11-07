
from datetime import date, datetime
from decimal import Decimal

from django.utils import timezone

from modeler.services.database_service import conectar_base_activa
from bi_agent.models import DashboardWidget, DashboardWidgetData
from bi_agent.services.sql_validator import validar_sql_consulta
from bi_agent.models import Dashboard, DashboardWidget, DashboardWidgetData


def serializar_valor(valor):
    """Convierte valores de PostgreSQL a tipos compatibles con JSON."""
    if isinstance(valor, (datetime, date)):
        return valor.isoformat()

    if isinstance(valor, Decimal):
        return float(valor)

    if isinstance(valor, bytes):
        return valor.decode("utf-8", errors="replace")

    return valor


def ejecutar_consulta_widget(sql):

    """
    Ejecuta una consulta de lectura y devuelve columnas y filas.
    La consulta debe superar el validador SQL.
    """
    sql_validado = validar_sql_consulta(sql)

    with conectar_base_activa() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(sql_validado)

            columnas = [
                descripcion.name
                for descripcion in cursor.description
            ]

            filas = cursor.fetchall()

    datos = [
        {
            columnas[indice]: serializar_valor(valor)
            for indice, valor in enumerate(fila)
        }
        for fila in filas
    ]

    return columnas, datos


def refrescar_widget(widget):
    """Ejecuta y guarda los resultados de un widget."""
    registro, _ = DashboardWidgetData.objects.get_or_create(
        widget=widget
    )

    try:
        columnas, datos = ejecutar_consulta_widget(widget.sql_query)

        registro.columns = columnas
        registro.data = datos
        registro.last_refreshed_at = timezone.now()
        registro.last_error = ""
        registro.save(
            update_fields=[
                "columns",
                "data",
                "last_refreshed_at",
                "last_error",
            ]
        )

        return {
            "widget": widget.key,
            "ok": True,
            "filas": len(datos),
        }

    except Exception as exc:
        registro.last_error = str(exc)
        registro.save(update_fields=["last_error"])

        return {
            "widget": widget.key,
            "ok": False,
            "error": str(exc),
        }


def refrescar_dashboard(dashboard):
    """Refresca todos los widgets habilitados de un dashboard."""
    resultados = []

    for widget in dashboard.widgets.filter(enabled=True).order_by("position"):
        resultados.append(refrescar_widget(widget))

    return resultados


from django.utils import timezone

from bi_agent.models import Dashboard, DashboardWidget
from bi_agent.services.dashboard_data_service import (
    refrescar_widget,
)


def controlador_datos(dashboard_id):
    """
    Ejecuta las consultas SQL de todos los widgets habilitados
    y almacena los resultados en DashboardWidgetData.

    Actualiza el estado del dashboard según el resultado.
    """

    # 1. Recuperar el dashboard y sus widgets
    try:
        dashboard = Dashboard.objects.prefetch_related(
            "widgets"
        ).get(pk=dashboard_id)

    except Dashboard.DoesNotExist:
        raise ValueError(
            f"No existe un dashboard con ID: {dashboard_id}"
        )

    widgets = list(
        dashboard.widgets.filter(
            enabled=True
        ).order_by("position")
    )

    if not widgets:
        dashboard.status = Dashboard.Status.ERROR
        dashboard.save(update_fields=["status", "updated_at"])

        return {
            "dashboard_id": str(dashboard.id),
            "success": False,
            "status": Dashboard.Status.ERROR,
            "error": "El dashboard no contiene widgets habilitados.",
        }

    # 2. Ejecutar y almacenar los resultados de cada widget
    resultados = []

    for widget in widgets:

        resultado = refrescar_widget(widget)

        resultados.append(resultado)

        print(
            f"Widget: {widget.key} | "
            f"Resultado: {resultado}"
        )

    # 3. Determinar si todos los widgets fueron procesados
    widgets_exitosos = sum(
        1 for resultado in resultados
        if resultado["ok"]
    )

    widgets_fallidos = len(resultados) - widgets_exitosos

    todo_correcto = widgets_fallidos == 0

    # 4. Actualizar estado del dashboard
    dashboard.status = (
        Dashboard.Status.READY
        if todo_correcto
        else Dashboard.Status.ERROR
    )

    dashboard.save(
        update_fields=["status", "updated_at"]
    )

    # 5. Retornar resultado del procesamiento
    return {
        "dashboard_id": str(dashboard.id),
        "success": todo_correcto,
        "status": dashboard.status,
        "total_widgets": len(widgets),
        "widgets_exitosos": widgets_exitosos,
        "widgets_fallidos": widgets_fallidos,
        "resultados": resultados,
    }
