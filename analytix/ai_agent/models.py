from django.db import models

class TablaContexto(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    alias = models.CharField(max_length=255, blank=True)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class ColumnaContexto(models.Model):
    tabla = models.ForeignKey(
        TablaContexto,
        on_delete=models.CASCADE,
        related_name="columnas"
    )
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=100)
    es_pk = models.BooleanField(default=False)
    es_fk = models.BooleanField(default=False)
    descripcion = models.TextField(blank=True)
    ejemplos = models.TextField(blank=True)

    class Meta:
        unique_together = ("tabla", "nombre")

    def __str__(self):
        return f"{self.tabla.nombre}.{self.nombre}"


class RelacionContexto(models.Model):
    tabla_origen = models.ForeignKey(
        TablaContexto,
        on_delete=models.CASCADE,
        related_name="relaciones_salientes"
    )
    columna_origen = models.CharField(max_length=255)

    tabla_destino = models.ForeignKey(
        TablaContexto,
        on_delete=models.CASCADE,
        related_name="relaciones_entrantes"
    )
    columna_destino = models.CharField(max_length=255)

    def __str__(self):
        return (
            f"{self.tabla_origen.nombre}.{self.columna_origen} → "
            f"{self.tabla_destino.nombre}.{self.columna_destino}"
        )