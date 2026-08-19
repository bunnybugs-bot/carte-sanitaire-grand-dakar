"""
serializers.py — Personne 3
============================

Sérialisation des modèles géographiques en GeoJSON pour l'app WebSIG.

Basé sur le models.py réel (Personne 2) :

    class Quartier(models.Model):
        nom = models.CharField(max_length=150)
        population_hommes = models.IntegerField(null=True, blank=True)
        population_femmes = models.IntegerField(null=True, blank=True)
        geom = models.PolygonField(srid=4326)

    class Etablissement(models.Model):
        TYPE_CHOICES = [...]  # poste_sante, centre_sante, hopital,
                               # centre_medico_social, pharmacie
        STATUT_CHOICES = [('public', 'Public'), ('prive', 'Privé')]

        nom = models.CharField(max_length=200)
        type_etablissement = models.CharField(max_length=30, choices=TYPE_CHOICES)
        statut = models.CharField(max_length=10, choices=STATUT_CHOICES, blank=True)
        quartier = models.ForeignKey(Quartier, on_delete=models.SET_NULL, null=True, blank=True)
        contact = models.CharField(max_length=100, blank=True)
        capacite = models.IntegerField(null=True, blank=True)
        geom = models.PointField(srid=4326)

⚠️ Le modèle Signalement (contribution citoyenne, voir forms.py) n'est
   pas encore dans ce models.py — à confirmer avec la Personne 2.
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
            "statut",           # 'public' ou 'prive'
            "statut_display",
            "contact",
            "capacite",
            "quartier",
            "quartier_nom",
        ]


class QuartierSerializer(GeoFeatureModelSerializer):
    """
    Sérialise les limites de quartiers (couche administrative de fond).
    Expose population_hommes / population_femmes séparément, ainsi
    qu'un total calculé pratique pour l'affichage côté front.
    """

    population_totale = serializers.SerializerMethodField()

    class Meta:
        model = Quartier
        geo_field = "geom"
        fields = ["id", "nom", "population_hommes", "population_femmes", "population_totale"]

    def get_population_totale(self, obj):
        hommes = obj.population_hommes or 0
        femmes = obj.population_femmes or 0
        if obj.population_hommes is None and obj.population_femmes is None:
            return None
        return hommes + femmes