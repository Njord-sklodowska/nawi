from django.urls import path
from . import views

urlpatterns = [
    path("objetos/", views.lista_objetos),
    path("objetos/<str:slug>/", views.detalle_objeto),
]
