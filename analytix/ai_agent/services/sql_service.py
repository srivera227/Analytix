from .llm_service import ask_llmGemini
from .llm_service import agent_sql
from .schema_service import obtener_schema


def generar_sql(pregunta,schema,tablasUsadas,columnastablas):
    print("Generando sql...")
    prompt = f""" 
    You are a PostgreSQL expert who generates secure and accurate SQL. 
    DATABASE SCHEMA: {schema} 
    TABLES SELECTED FOR THE USER: {tablasUsadas} 
    TABLE COLUMNS AND DATA TYPES: {columnastablas} 
    USER QUESTION: {pregunta} 
    MANDATORY POSTGRESQL IDENTIFIER RULES: 
    1. PostgreSQL converts unquoted identifiers to lowercase. 
    2. Preserve the exact spelling and capitalization of every table and column name provided in the schema. 
    3. ALWAYS enclose column names containing uppercase letters in double quotes. 
    4. ALWAYS enclose table names containing uppercase letters in double quotes. 
    5. Never change the capitalization of an identifier. 
    6. Apply these rules to every occurrence of an identifier, including SELECT, WHERE, ORDER BY, GROUP BY, JOIN and aliases when applicable. 
    7. Do not quote identifiers that are entirely lowercase unless required by PostgreSQL syntax. 
    8. Double quotes are for identifiers, not string values. 
    EXAMPLE: 
    Incorrect: SELECT * FROM asignacion_turnos_empleado_oddo ORDER BY fechaIngreso DESC LIMIT 5; 
    Correct: SELECT * FROM asignacion_turnos_empleado_oddo ORDER BY "fechaIngreso" DESC LIMIT 5; 
    STRICT SECURITY RULES: 
    1. Generate exactly one read-only SELECT query. 
    2. Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE or other data-modifying statements. 
    3. Do not generate multiple SQL statements. 
    4. Use only tables and columns present in the supplied schema. 
    5. Do not invent table names or column names. 
    6. Do not include explanations, comments or Markdown. 
    7. Return only the SQL query. Convert the user's question into a PostgreSQL query. Respond with SQL only. """

    sql = agent_sql(prompt)
    return sql