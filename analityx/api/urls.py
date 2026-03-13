from django.urls import path
from .views import ai_query

urlpatterns = [
    path("ai_query/", ai_query),
]