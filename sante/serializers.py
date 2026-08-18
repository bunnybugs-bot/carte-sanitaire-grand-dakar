"""
serializers.py — Personne 3
============================

Sérialisation des modèles géographiques en GeoJSON pour l'app WebSIG.

⚠️ HYPOTHÈSES SUR LES MODÈLES (à ajuster dès que le vrai models.py
   de la Personne 2 est disponible) :

    class Quartier(models.Model):
        nom = models.CharField(max_length=150)
        population = models.IntegerField(null=True, blank=True)
        geom = models.PolygonField(srid=4326)

    class Etablissement(models.Model):
        TYPE_CHOICES = [
            ("poste_sante", "Poste de santé"),
            ("centre_sante", "Centre de santé"),
            ("hopital", "Hôpital"),
            ("clinique", "Clinique"),
            ("pharmacie", "Pharmacie"),
        ]
        SECTEUR_CHOICES = [
            ("public", "Public"),
            ("prive", "Privé"),
        ]
        STATUT_CHOICES = [
            ("actif", "Actif"),
            ("ferme", "Fermé"),
            ("en_projet", "En projet"),
        ]

        nom = models.CharField(max_length=200)
        type_etablissement = models.CharField(max_length=30, choices=TYPE_CHOICES)
        secteur = models.CharField(max_length=10, choices=SECTEUR_CHOICES)
        statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="actif")
        contact = models.CharField(max_length=100, blank=True, null=True)
        capacite_lits = models.IntegerField(blank=True, null=True)
        quartier = models.ForeignKey(Quartier, on_delete=models.SET_NULL, null=True)
        geom = models.PointField(srid=4326)

Si les noms de champs réels diffèrent, il suffit d'adapter la liste
`fields` / `geo_field` ci-dessous — la logique ne change pas.
"""

from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers

from .models import Etablissement, Quartier


class EtablissementSerializer(GeoFeatureModelSerializer):
    """
    Sérialise chaque établissement en Feature GeoJSON.
    Le front (Leaflet) consomme directement cette sortie via
    L.geoJSON(data) sans transformation supplémentaire.
    """

    type_display = serializers.CharField(source="get_type_etablissement_display", read_only=True)
    secteur_display = serializers.CharField(source="get_secteur_display", read_only=True)
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)
    quartier_nom = serializers.CharField(source="quartier.nom", read_only=True, default=None)

    class Meta:
        model = Etablissement
        geo_field = "geom"
        fields = [
            "id",
            "nom",
            "type_etablissement",
            "type_display",
            "secteur",
            "secteur_display",
            "statut",
            "statut_display",
            "contact",
            "capacite_lits",
            "quartier_nom",
        ]


class QuartierSerializer(GeoFeatureModelSerializer):
    """
    Sérialise les limites de quartiers (couche administrative de fond).
    """

    class Meta:
        model = Quartier
        geo_field = "geom"
        fields = ["id", "nom", "population"]