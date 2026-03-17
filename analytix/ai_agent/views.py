from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services import bi_agent


def vistaHome(request):
    if request.method == "GET":
        return render(request,"account/home.html")
    

@api_view(["POST"])
def ai_query(request):

    pregunta = request.data["pregunta"]
    print(f"Pregunta: {pregunta}")

    r = bi_agent(pregunta)

    return Response({
        "respuesta": r
    })


