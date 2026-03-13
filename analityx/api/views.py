from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from services.bi_agent import bi_agent

@api_view(["POST"])
def ai_query(request):

    pregunta = request.data["pregunta"]
    print(f"Pregunta: {pregunta}")

    r = bi_agent(pregunta)

    return Response({
        "respuesta": r
    })
