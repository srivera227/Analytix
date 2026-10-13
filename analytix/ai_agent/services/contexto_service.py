from django.db import transaction

from ..models import (
    TablaContexto,
    ColumnaContexto,
)

from .schema_service import obtener_schema


@transaction.atomic
def sincronizar_schema():

    schema = obtener_schema()

    for nombre_tabla, columnas in schema.items():

        tabla, _ = TablaContexto.objects.update_or_create(
            nombre=nombre_tabla,
            defaults={
                "activa": True,
            }
        )

        columnas_actuales = set()

        for columna in columnas:

            nombre_columna = columna["column"]

            columnas_actuales.add(nombre_columna)

            ColumnaContexto.objects.update_or_create(
                tabla=tabla,
                nombre=nombre_columna,
                defaults={
                    "tipo": columna["type"],
                    "es_pk": columna["es_pk"],
                    "es_fk": columna["es_fk"],
                }
            )

        # Opcionalmente podemos desactivar columnas
        # que ya no existan en la BD.

    return len(schema)