"""
urls.py — Personne 3
======================

Routes de l'app `sante`. À inclure dans config/urls.py (Personne 2/3)
via :

    from django.urls import path, include
    urlpatterns = [
        ...
        path("", include("sante.urls")),
    ]
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"api/etablissements", views.EtablissementViewSet, basename="etablissement")
router.register(r"api/quartiers", views.QuartierViewSet, basename="quartier")

urlpatterns = [
    # Page carte (rendue côté serveur, front géré par la Personne 4)
    path("", views.carte_view, name="carte"),

    # Contribution citoyenne
    path("api/signalement/", views.signalement_view, name="signalement"),

    # Endpoints GeoJSON (établissements + quartiers), générés par le router
    path("", include(router.urls)),
]