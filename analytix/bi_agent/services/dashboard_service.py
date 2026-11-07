
from django.db import transaction
from django.utils import timezone

from modeler.models import ConexionBase

from bi_agent.models import (
    Dashboard,
    DashboardWidget,
    DashboardWidgetData,
)


from bi_agent.services.dashboard_ai_service import (
    generar_dashboard_general,
)
from bi_agent.services.sql_validator import validar_sql_consulta


def obtener_conexion_activa():
    conexiones = list(
        ConexionBase.objects.filter(status=True)[:2]
    )

    if not conexiones:
        raise ValueError("No hay una conexión activa configurada.")

    if len(conexiones) > 1:
        raise ValueError(
            "Existe más de una conexión activa. "
            "Debe haber una sola."
        )

    return conexiones[0]


def obtener_o_generar_dashboard_general(esquema):
    """
    Recupera el dashboard general de la conexión activa.
    Si no existe, genera y persiste su definición.

    Este método no ejecuta las consultas SQL de los widgets.
    """
    if not isinstance(esquema, dict):
        raise ValueError("El esquema recibido no tiene un formato válido.")

    if esquema.get("error"):
        raise ValueError(esquema["error"])

    tablas = esquema.get("tablas", [])

    if not isinstance(tablas, list) or not tablas:
        raise ValueError("No existen tablas para generar el dashboard.")

    print("Obteniendo conexión activa...")
    conexion = obtener_conexion_activa()
    

    existente = Dashboard.objects.filter(
        connection=conexion,
        dashboard_type=Dashboard.DashboardType.GENERAL,
    ).first()

    if existente and existente.status == Dashboard.Status.READY:
        return existente, False

    # Si hay un dashboard previo en estado de error o generación,
    # no lo sobrescribimos automáticamente ni llamamos a Claude.
    if existente:
        raise ValueError(
            f"El dashboard existe con estado '{existente.status}'. "
            "Debe revisarse antes de intentar generarlo nuevamente."
        )

    print("Generando dashboard...")
    definicion = generar_dashboard_general(esquema)

    # Validar todas las consultas antes de persistir el dashboard.
    widgets_validados = []

    for widget in definicion["widgets"]:
        sql_validado = validar_sql_consulta(
            widget["sql_query"]
        )

        widgets_validados.append({
            **widget,
            "sql_query": sql_validado,
        })

    with transaction.atomic():
        dashboard = Dashboard.objects.create(
            connection=conexion,
            name=definicion["name"],
            dashboard_type=Dashboard.DashboardType.GENERAL,
            status=Dashboard.Status.GENERATING,
            definition={
                "schema_tables": [
                    tabla["tabla"] for tabla in esquema.get("tablas", [])
                ],
            },
            last_generated_at=timezone.now(),
        )

        for widget in widgets_validados:
            widget_obj = DashboardWidget.objects.create(
                dashboard=dashboard,
                key=widget["key"],
                title=widget["title"],
                description=widget.get("description", ""),
                widget_type=widget["widget_type"],
                sql_query=widget["sql_query"],
                config=widget.get("config", {}),
                position=widget.get("position", 0),
            )

            DashboardWidgetData.objects.create(
                widget=widget_obj,
                data=[],
                columns=[],
            )

        dashboard.status = Dashboard.Status.READY
        dashboard.save(update_fields=["status", "updated_at"])

    return dashboard, True
