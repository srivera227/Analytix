from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services.bi_agent import bi_agent
from modeler.services.schema_service import obtener_columnas



def vistaHome(request):
    if request.method == "GET":
        return render(request,"account/home.html")
    

@api_view(["POST"])
def ai_query(request):

    pregunta = request.data["pregunta"]
    print(f"Pregunta: {pregunta}")

    schema = request.data.get("schema")
    tablasUsadas = request.data.get("tablasUsadas")
    columnastablas = dict(obtener_columnas(tablasUsadas))

    r = bi_agent(pregunta,schema,tablasUsadas,columnastablas)

    return Response({
        "respuesta": r
    })






