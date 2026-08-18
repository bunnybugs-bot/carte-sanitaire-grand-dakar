"""
views.py — Personne 3
=======================

Vues exposant les établissements et quartiers en GeoJSON, avec
recherche par nom et filtres (type, secteur, statut, quartier).

Endpoints prévus :
    GET /api/etablissements/                -> liste (GeoJSON FeatureCollection)
    GET /api/etablissements/?q=texte         -> recherche par nom
    GET /api/etablissements/?type=hopital    -> filtre par type
    GET /api/etablissements/?secteur=public  -> filtre par secteur
    GET /api/etablissements/?statut=actif    -> filtre par statut
    GET /api/etablissements/?quartier=<id>   -> filtre par quartier
    GET /api/etablissements/<id>/            -> détail (fiche établissement)
    GET /api/quartiers/                      -> couche administrative
    POST /api/signalement/                   -> contribution citoyenne (voir forms.py)
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
    contribution citoyenne (voir signalement_view ci-dessous),
    pas directement par l'API.
    """

    queryset = Etablissement.objects.select_related("quartier").all()
    serializer_class = EtablissementSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["type_etablissement", "secteur", "statut", "quartier"]
    search_fields = ["nom"]  # -> ?search=texte (recherche par nom)

    def get_queryset(self):
        qs = super().get_queryset()
        # Recherche libre optionnelle via ?q= en plus de ?search=
        # (au cas où le front utilise q= plutôt que le search DRF standard)
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

    Ne crée PAS directement un Etablissement en base (pas de
    validation automatique des contributions anonymes) : enregistre
    la proposition pour modération, en attendant que la Personne 2
    décide du modèle de stockage (ex: modèle Signalement séparé).
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
    la carte Leaflet. Le template lui-même est géré par la Personne 4
    (templates/sante/carte.html), cette vue se contente de le rendre
    avec un minimum de contexte.
    """
    context = {
        "types_etablissement": Etablissement.TYPE_CHOICES if hasattr(Etablissement, "TYPE_CHOICES") else [],
    }
    return render(request, "sante/carte.html", context)