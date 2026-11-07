
from modeler.services.database_service import conectar_base_activa


MAX_TABLES = 100
MAX_COLUMNS_PER_TABLE = 80
MAX_CATEGORY_VALUES = 15
MAX_DISTINCT_CATEGORY = 30


def _identificador_sql(nombre):
    """Escapa un identificador SQL de PostgreSQL."""
    return '"' + nombre.replace('"', '""') + '"'


def _clasificar_columna(
    nombre,
    tipo,
    valores_distintos,
    total_registros,
    es_pk=False,
    es_fk=False,
    valores=None,
):
    """
    Clasifica una columna según su nombre, tipo y contenido.
    No modifica los valores originales.
    """
    nombre_lower = nombre.lower()
    tipo_lower = tipo.lower()
    valores = valores or []

    nombres_id = (
        nombre_lower == "id"
        or nombre_lower.endswith("_id")
        or nombre_lower.startswith("id_")
        or nombre_lower.endswith("_uuid")
    )

    nombres_estado = any(
        palabra in nombre_lower
        for palabra in ("estado", "status", "situacion")
    )

    nombres_categoria = any(
        palabra in nombre_lower
        for palabra in (
            "tipo", "categoria", "category", "cargo",
            "rol", "prioridad", "modalidad", "jornada",
        )
    )

    nombres_fecha = any(
        palabra in nombre_lower
        for palabra in ("fecha", "date", "created_at", "updated_at")
    )

    nombres_descriptivos = any(
        palabra in nombre_lower
        for palabra in (
            "nombre", "name", "descripcion", "description",
            "observacion", "comentario", "direccion",
        )
    )

    tipos_temporales = (
        "date",
        "timestamp",
        "time",
        "interval",
    )

    tipos_numericos = (
        "smallint",
        "integer",
        "bigint",
        "numeric",
        "decimal",
        "real",
        "double precision",
    )

    tipos_texto = (
        "character varying",
        "character",
        "text",
        "USER-DEFINED",
        "enum",
    )

    # Primero, tipos de negocio que se pueden reconocer con confianza.
    if es_pk or es_fk or nombres_id:
        categoria = "identifier"
        subcategoria = (
            "primary_key" if es_pk
            else "foreign_key" if es_fk
            else "business_identifier"
        )

    elif nombres_fecha or any(
        tipo_lower.startswith(t) for t in tipos_temporales
    ):
        categoria = "datetime"
        subcategoria = "date_or_time"

    elif tipo_lower == "boolean":
        categoria = "boolean"
        subcategoria = "binary_category"

    elif nombres_estado:
        categoria = "category"
        subcategoria = "business_status"

    elif nombres_categoria:
        categoria = "category"
        subcategoria = "business_category"

    elif nombres_descriptivos:
        categoria = "descriptive"
        subcategoria = "text_description"

    elif any(tipo_lower.startswith(t) for t in tipos_numericos):
        if (
            valores_distintos > 0
            and valores_distintos <= MAX_DISTINCT_CATEGORY
            and total_registros > 0
            and valores_distintos / total_registros <= 0.20
        ):
            categoria = "category"
            subcategoria = "low_cardinality_numeric"
        else:
            categoria = "metric"
            subcategoria = "numeric_measure"

    elif (
        any(tipo_lower.startswith(t) for t in tipos_texto)
        and valores_distintos <= MAX_DISTINCT_CATEGORY
    ):
        categoria = "category"
        subcategoria = "nominal_category"

    elif any(tipo_lower.startswith(t) for t in tipos_texto):
        categoria = "descriptive"
        subcategoria = "high_cardinality_text"

    else:
        categoria = "other"
        subcategoria = "unclassified"

    # Evitamos crear filtros generales para columnas de alta cardinalidad.
    es_filtrable = categoria in {
        "category",
        "boolean",
        "datetime",
    }

    if categoria == "category" and valores_distintos > MAX_DISTINCT_CATEGORY:
        es_filtrable = False

    # Una clave foránea puede servir para segmentar si tiene sentido
    # mostrar las entidades relacionadas en el dashboard.
    if es_fk:
        es_filtrable = True

    return {
        "categoria": categoria,
        "subcategoria": subcategoria,
        "es_filtrable": es_filtrable,
        "es_metrica": categoria == "metric",
        "es_dimension": categoria in {
            "category",
            "boolean",
            "datetime",
        },
    }


def _normalizar_significado_estado(valor):
    """
    Sugiere una interpretación visual genérica del estado.
    El valor original se conserva siempre.
    """
    if valor is None:
        return None

    texto = str(valor).strip().lower()

    equivalencias = {
        "aprobado": "aprobado",
        "aprobada": "aprobado",
        "approved": "aprobado",
        "aceptado": "aprobado",
        "aceptada": "aprobado",

        "rechazado": "rechazado",
        "rechazada": "rechazado",
        "rejected": "rechazado",
        "denegado": "rechazado",
        "denegada": "rechazado",

        "pendiente": "pendiente",
        "pending": "pendiente",
        "en espera": "pendiente",

        "cancelado": "cancelado",
        "cancelada": "cancelado",
        "cancelled": "cancelado",
        "canceled": "cancelado",
    }

    return equivalencias.get(texto)


def analizar_tablas_seleccionadas(nombres_tablas):
    """
    Analiza exclusivamente las tablas seleccionadas de la base activa.

    Devuelve estructura, claves, relaciones y perfil semántico
    de las columnas. Solo realiza consultas de lectura.
    """
    nombres_tablas = list(dict.fromkeys(nombres_tablas or []))

    if not nombres_tablas:
        return {
            "tablas": [],
            "relaciones": [],
            "error": "Debes seleccionar al menos una tabla.",
        }

    if len(nombres_tablas) > MAX_TABLES:
        return {
            "tablas": [],
            "relaciones": [],
            "error": f"Máximo permitido: {MAX_TABLES} tablas.",
        }

    esquema = []
    relaciones = []

    with conectar_base_activa() as conexion:
        with conexion.cursor() as cursor:

            # Validar que todas las tablas existan en public.
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
                  AND table_name = ANY(%s)
                """,
                (nombres_tablas,),
            )

            tablas_validas = {fila[0] for fila in cursor.fetchall()}
            tablas_invalidas = sorted(set(nombres_tablas) - tablas_validas)

            if tablas_invalidas:
                return {
                    "tablas": [],
                    "relaciones": [],
                    "error": (
                        "Tablas inexistentes o no permitidas: "
                        + ", ".join(tablas_invalidas)
                    ),
                }

            # Identificar PK y FK de las tablas seleccionadas.
            cursor.execute(
                """
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    tc.constraint_type,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                  ON tc.constraint_catalog = kcu.constraint_catalog
                 AND tc.constraint_schema = kcu.constraint_schema
                 AND tc.constraint_name = kcu.constraint_name
                 AND tc.table_name = kcu.table_name
                LEFT JOIN information_schema.constraint_column_usage ccu
                  ON tc.constraint_catalog = ccu.constraint_catalog
                 AND tc.constraint_schema = ccu.constraint_schema
                 AND tc.constraint_name = ccu.constraint_name
                WHERE tc.constraint_schema = 'public'
                  AND tc.table_name = ANY(%s)
                  AND tc.constraint_type IN ('PRIMARY KEY', 'FOREIGN KEY')
                ORDER BY tc.table_name, kcu.ordinal_position
                """,
                (nombres_tablas,),
            )

            filas_constraints = cursor.fetchall()

            claves_primarias = {}
            claves_foraneas = {}
            for tabla, columna, tipo_constraint, tabla_ref, columna_ref in filas_constraints:
                if tipo_constraint == "PRIMARY KEY":
                    claves_primarias.setdefault(tabla, set()).add(columna)

                elif tipo_constraint == "FOREIGN KEY":
                    claves_foraneas.setdefault(tabla, set()).add(columna)

                    # Solo incluimos relaciones entre tablas seleccionadas.
                    if tabla_ref in tablas_validas:
                        relacion = {
                            "tabla_origen": tabla,
                            "columna_origen": columna,
                            "tabla_destino": tabla_ref,
                            "columna_destino": columna_ref,
                            "tipo": "foreign_key",
                            "confirmada": True,
                        }

                        if relacion not in relaciones:
                            relaciones.append(relacion)

            # Analizar cada tabla seleccionada.
            for tabla in nombres_tablas:
                tabla_sql = _identificador_sql(tabla)

                cursor.execute(
                    f"SELECT COUNT(*) FROM public.{tabla_sql}"
                )
                total_registros = cursor.fetchone()[0]

                cursor.execute(
                    """
                    SELECT column_name, data_type, is_nullable,
                           udt_name, ordinal_position
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = %s
                    ORDER BY ordinal_position
                    LIMIT %s
                    """,
                    (tabla, MAX_COLUMNS_PER_TABLE),
                )

                filas_columnas = cursor.fetchall()
                columnas_resultado = []

                for nombre, tipo, nullable, udt_name, posicion in filas_columnas:
                    columna_sql = _identificador_sql(nombre)

                    # Perfil básico de cada columna.
                    cursor.execute(
                        f"""
                        SELECT
                            COUNT(DISTINCT {columna_sql}),
                            COUNT(*) FILTER (
                                WHERE {columna_sql} IS NULL
                            )
                        FROM public.{tabla_sql}
                        """
                    )

                    valores_distintos, nulos = cursor.fetchone()
                    valores_distintos = valores_distintos or 0

                    es_pk = nombre in claves_primarias.get(tabla, set())
                    es_fk = nombre in claves_foraneas.get(tabla, set())

                    # Obtener frecuencias para tipos que suelen contener
                    # categorías. Los valores se conservan como texto.
                    valores = []
                    tipos_categorizables = {
                        "character varying",
                        "character",
                        "text",
                        "boolean",
                        "USER-DEFINED",
                        "smallint",
                        "integer",
                    }

                    if (
                        tipo in tipos_categorizables
                        and valores_distintos <= MAX_DISTINCT_CATEGORY
                    ):
                        cursor.execute(
                            f"""
                            SELECT {columna_sql}::text, COUNT(*) AS cantidad
                            FROM public.{tabla_sql}
                            GROUP BY {columna_sql}
                            ORDER BY cantidad DESC
                            LIMIT %s
                            """,
                            (MAX_CATEGORY_VALUES,),
                        )

                        valores = [
                            {
                                "valor": valor,
                                "cantidad": cantidad,
                            }
                            for valor, cantidad in cursor.fetchall()
                        ]

                    clasificacion = _clasificar_columna(
                        nombre=nombre,
                        tipo=tipo,
                        valores_distintos=valores_distintos,
                        total_registros=total_registros,
                        es_pk=es_pk,
                        es_fk=es_fk,
                        valores=valores,
                    )

                    # Añadir interpretación semántica a estados conocidos.
                    if clasificacion["subcategoria"] == "business_status":
                        for item in valores:
                            item["grupo_semantico"] = (
                                _normalizar_significado_estado(item["valor"])
                            )

                    columnas_resultado.append({
                        "nombre": nombre,
                        "tipo": tipo,
                        "tipo_postgresql": udt_name,
                        "posicion": posicion,
                        "nullable": nullable == "YES",
                        "es_pk": es_pk,
                        "es_fk": es_fk,
                        "total_registros": total_registros,
                        "valores_distintos": valores_distintos,
                        "nulos": nulos,
                        "porcentaje_nulos": (
                            round(nulos / total_registros * 100, 2)
                            if total_registros else 0
                        ),
                        "valores": valores,
                        **clasificacion,
                    })

                esquema.append({
                    "tabla": tabla,
                    "total_registros": total_registros,
                    "columnas": columnas_resultado,
                })

    return {
        "tablas": esquema,
        "relaciones": relaciones,
        "error": None,
    }
