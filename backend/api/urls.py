from django.urls import path

from . import views

urlpatterns = [
    path("estado/", views.estado_api, name="estado_api"),
    path("objetos/", views.listar_objetos, name="listar_objetos"),
    path("objetos/<slug:slug>/", views.detalle_objeto, name="detalle_objeto"),
    path(
        "objetos/<slug:slug>/posicion/",
        views.posicion_objeto,
        name="posicion_objeto",
    ),
    path(
        "objetos/<slug:slug>/cuadros/",
        views.cuadros_objeto,
        name="cuadros_objeto",
    ),
]
