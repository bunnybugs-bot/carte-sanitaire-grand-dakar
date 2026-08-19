"""
views.py — Personne 3
=======================

Vues exposant les établissements et quartiers en GeoJSON, avec
recherche par nom et filtres (type, statut public/privé, quartier).

Endpoints :
    GET /api/etablissements/                 -> liste (GeoJSON FeatureCollection)
    GET /api/etablissements/?search=texte     -> recherche par nom
    GET /api/etablissements/?type_etablissement=hopital -> filtre par type
    GET /api/etablissements/?statut=public    -> filtre public/privé
    GET /api/etablissements/?quartier=<id>    -> filtre par quartier
    GET /api/etablissements/<id>/             -> détail (fiche établissement)
    GET /api/quartiers/                       -> couche administrative
    POST /api/signalement/                    -> contribution citoyenne (voir forms.py)
"""

from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Etablissement, Quartier
from .serializers import EtablissementSerializer, QuartierSerializer
from .forms import SignalementForm


class EtablissementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Expose les établissements de santé en GeoJSON.
    Lecture seule : la création passe par le formulaire de
    contribution citoyenne, pas directement par l'API.
    """

    queryset = Etablissement.objects.select_related("quartier").all()
    serializer_class = EtablissementSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["type_etablissement", "statut", "quartier"]
    search_fields = ["nom"]  # -> ?search=texte

    def get_queryset(self):
        qs = super().get_queryset()
        # Recherche libre optionnelle via ?q= en plus de ?search=
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(nom__icontains=q)
        return qs


class QuartierViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Expose les limites de quartiers (couche de fond administrative).
    """

    queryset = Quartier.objects.all()
    serializer_class = QuartierSerializer


@api_view(["POST"])
def signalement_view(request):
    """
    Réception d'une contribution citoyenne : signalement d'un
    établissement manquant ou mise à jour d'informations.

    ⚠️ Dépend du modèle Signalement (voir forms.py), pas encore
    présent dans models.py — à confirmer avec la Personne 2 avant
    de fusionner cette fonctionnalité.
    """

    form = SignalementForm(request.data)
    if form.is_valid():
        signalement = form.save(commit=False)
        signalement.statut_moderation = "en_attente"
        signalement.save()
        return Response(
            {"message": "Signalement enregistré, en attente de modération."},
            status=201,
        )
    return Response(form.errors, status=400)


def carte_view(request):
    """
    Vue "page" classique (non-API) qui sert le template contenant
    la carte Leaflet. Le template lui-même est géré par la Personne 4.
    """
    context = {
        "types_etablissement": Etablissement.TYPE_CHOICES,
        "statuts": Etablissement.STATUT_CHOICES,
    }
    return render(request, "sante/carte.html", context)