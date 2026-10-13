from .llm_service import agent_sql
from .db_service import ejecutar_sql
from .validator_sql import validar_sql
from .sql_service import generar_sql


def bi_agent(pregunta,schema,tablasUsadas,columnastablas):
    print(f"Ejecutanto el agente...")
    # 1 generar sql
    sql = generar_sql(pregunta,schema,tablasUsadas,columnastablas)

    sql = validar_sql(sql)

    # 2 ejecutar
    resultado = ejecutar_sql(sql)

    # 3 responder con datos (NO explicar)
    respuesta = agent_sql(
        prompt = f"""
        You are AnalytiX, a fast and accurate data assistant. 
        QUESTION: {pregunta} 
        DATA: {resultado} 
        RULES: 
        1. Answer the question directly directly in Spanish. 
        2. Use only the provided data. 
        3. Organize the information clearly, concisely, and naturally. 
        4. Do not use Markdown, tables, lists, headings, or decorations. 
        5. Do not include unnecessary introductions, in-depth explanations, or conclusions. 
        6. For multiple records, present each record on separate lines. 
        7. Highlight only relevant information. 
        8. If there are no results, state this briefly. 
        9. Do not invent or modify data. - You can use *, -, | to structure the answer.
        """
        )
    

    return respuesta