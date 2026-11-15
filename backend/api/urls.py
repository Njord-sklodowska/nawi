from django.urls import path
from . import views

urlpatterns = [
    path("estado/", views.estado_api),
    path("objetos/", views.lista_objetos),
    path("objetos/<slug:slug>/", views.detalle_objeto),
    path("objetos/<slug:slug>/catalogo/", views.catalogo_objeto),
    path("objetos/<slug:slug>/posicion/", views.posicion_objeto),
]