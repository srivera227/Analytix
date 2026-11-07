
import sqlglot
from sqlglot import exp


def validar_sql_consulta(sql: str) -> str:
    """
    Valida que la consulta sea una única sentencia SELECT de PostgreSQL.
    No ejecuta la consulta.
    """
    if not isinstance(sql, str) or not sql.strip():
        raise ValueError("La consulta SQL está vacía.")

    try:
        sentencias = sqlglot.parse(sql, read="postgres")
    except sqlglot.errors.ParseError as exc:
        raise ValueError("La consulta SQL tiene una sintaxis inválida.") from exc

    sentencias = [sentencia for sentencia in sentencias if sentencia is not None]

    if len(sentencias) != 1:
        raise ValueError("Solo se permite una sentencia SQL por consulta.")

    consulta = sentencias[0]

    # Aceptar SELECT y consultas WITH que terminen en SELECT.
    if not isinstance(consulta, (exp.Select, exp.Union, exp.Intersect, exp.Except)):
        if not isinstance(consulta, exp.Query):
            raise ValueError("Solo se permiten consultas de lectura.")

    # Bloquear operaciones y construcciones que puedan modificar datos.
    operaciones_prohibidas = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Alter,
        exp.Create,
        exp.Merge,
        exp.Command,
    )

    for nodo in consulta.walk():
        if isinstance(nodo, operaciones_prohibidas):
            raise ValueError("La consulta contiene una operación no permitida.")

    return consulta.sql(dialect="postgres")
