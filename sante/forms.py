"""
forms.py — Personne 3
=======================

Formulaire pour la fonctionnalité bonus "Système de contribution
citoyenne (signalement, mise à jour participative)" du cahier des
charges (section 4.2).

⚠️ HYPOTHÈSE : un modèle Signalement séparé (pas directement dans
   Etablissement) pour ne pas polluer les données validées avec des
   contributions non modérées. À faire valider par la Personne 2 :

    class Signalement(models.Model):
        TYPE_SIGNALEMENT = [
            ("nouvel_etablissement", "Nouvel établissement"),
            ("mise_a_jour", "Mise à jour d'un établissement existant"),
            ("erreur", "Signalement d'erreur"),
        ]
        STATUT_MODERATION = [
            ("en_attente", "En attente"),
            ("valide", "Validé"),
            ("rejete", "Rejeté"),
        ]

        type_signalement = models.CharField(max_length=30, choices=TYPE_SIGNALEMENT)
        etablissement_concerne = models.ForeignKey(
            "Etablissement", null=True, blank=True, on_delete=models.SET_NULL
        )
        nom_propose = models.CharField(max_length=200, blank=True)
        type_etablissement_propose = models.CharField(max_length=30, blank=True)
        description = models.TextField()
        geom = models.PointField(srid=4326, null=True, blank=True)
        contact_signaleur = models.EmailField(blank=True)
        statut_moderation = models.CharField(
            max_length=20, choices=STATUT_MODERATION, default="en_attente"
        )
        date_creation = models.DateTimeField(auto_now_add=True)
"""

from django import forms
from django.contrib.gis.geos import Point

from .models import Signalement


class SignalementForm(forms.ModelForm):
    """
    Formulaire de contribution citoyenne. Accepte soit :
    - un nouvel établissement à proposer (nom_propose + type)
    - une mise à jour d'un établissement existant (etablissement_concerne)
    - un signalement d'erreur libre (description seule)

    La géométrie est reçue en lat/lon séparés côté client (plus simple
    pour un formulaire HTML classique) et recomposée en Point ici.
    """

    latitude = forms.FloatField(required=False)
    longitude = forms.FloatField(required=False)

    class Meta:
        model = Signalement
        fields = [
            "type_signalement",
            "etablissement_concerne",
            "nom_propose",
            "type_etablissement_propose",
            "description",
            "contact_signaleur",
        ]

    def clean(self):
        cleaned_data = super().clean()
        type_signalement = cleaned_data.get("type_signalement")

        if type_signalement == "nouvel_etablissement" and not cleaned_data.get("nom_propose"):
            self.add_error("nom_propose", "Le nom est requis pour un nouvel établissement.")

        if type_signalement == "mise_a_jour" and not cleaned_data.get("etablissement_concerne"):
            self.add_error(
                "etablissement_concerne",
                "Précisez quel établissement est concerné par la mise à jour.",
            )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        lat = self.cleaned_data.get("latitude")
        lon = self.cleaned_data.get("longitude")
        if lat is not None and lon is not None:
            instance.geom = Point(lon, lat, srid=4326)
        if commit:
            instance.save()
        return instance