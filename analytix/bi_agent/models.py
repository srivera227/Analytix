from django.db import models
import uuid



class Dashboard(models.Model):
    class DashboardType(models.TextChoices):
        GENERAL = "general", "General"
        CUSTOM = "custom", "Personalizado"

    class Status(models.TextChoices):
        GENERATING = "generating", "Generando"
        READY = "ready", "Disponible"
        ERROR = "error", "Error"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    connection = models.ForeignKey(
        "modeler.ConexionBase",
        on_delete=models.CASCADE,
        related_name="dashboards",
    )

    name = models.CharField(max_length=150)
    dashboard_type = models.CharField(
        max_length=20,
        choices=DashboardType.choices,
        default=DashboardType.GENERAL,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.GENERATING,
    )

    schema_fingerprint = models.CharField(
        max_length=64,
        blank=True,
    )

    definition = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_generated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["connection", "dashboard_type"],
                name="unique_dashboard_type_per_connection",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.connection.dbname})"


class DashboardWidget(models.Model):
    class WidgetType(models.TextChoices):
        KPI = "kpi", "Indicador KPI"
        BAR = "bar", "Barras"
        LINE = "line", "Líneas"
        PIE = "pie", "Circular"
        DONUT = "donut", "Dona"
        AREA = "area", "Área"
        TABLE = "table", "Tabla"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name="widgets",
    )

    key = models.SlugField(max_length=100)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    widget_type = models.CharField(
        max_length=20,
        choices=WidgetType.choices,
    )

    sql_query = models.TextField()
    config = models.JSONField(default=dict, blank=True)

    position = models.PositiveIntegerField(default=0)
    enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["dashboard", "key"],
                name="unique_widget_key_per_dashboard",
            )
        ]

    def __str__(self):
        return f"{self.dashboard.name} - {self.title}"


class DashboardWidgetData(models.Model):
    widget = models.OneToOneField(
        DashboardWidget,
        on_delete=models.CASCADE,
        related_name="data",
    )

    data = models.JSONField(default=list, blank=True)
    columns = models.JSONField(default=list, blank=True)

    last_refreshed_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)

    def __str__(self):
        return f"Datos: {self.widget.title}"

