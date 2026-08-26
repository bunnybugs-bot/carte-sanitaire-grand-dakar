from django import forms
from django.contrib.gis.geos import Point
from django.db.models import Max
from .models import Etablissement


class EtablissementForm(forms.Form):
    AMENITY_CHOICES = [
        ('Poste de santé', 'Poste de santé'),
        ('Centre de santé', 'Centre de santé'),
        ('Hôpital public', 'Hôpital public'),
        ('Centre médico social', 'Centre médico social'),
        ('Pharmacie', 'Pharmacie'),
        ('Clinique', 'Clinique'),
    ]

    name = forms.CharField(
        label="Nom de l'établissement", max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    amenity = forms.ChoiceField(
        label="Type", choices=AMENITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    quartier = forms.CharField(
        label="Quartier", max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    latitude = forms.FloatField(
        label="Latitude (WGS84)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'id': 'id_latitude'})
    )
    longitude = forms.FloatField(
        label="Longitude (WGS84)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'id': 'id_longitude'})
    )

    def save(self):
        # 1. Créer le point dans le système où l'utilisateur saisit (GPS classique)
        point_4326 = Point(self.cleaned_data['longitude'], self.cleaned_data['latitude'], srid=4326)
        # 2. Reprojeter vers le système utilisé en base (UTM 28N)
        point_4326.transform(32628)
# Calcul manuel du prochain id (table sans auto-increment)
        max_id = Etablissement.objects.aggregate(Max('id'))['id__max'] or 0
        next_id = max_id + 1
        
        etablissement = Etablissement(
            id=next_id,
            name=self.cleaned_data['name'],
            amenity=self.cleaned_data['amenity'],
            quartier=self.cleaned_data['quartier'],
            geom=point_4326,
        )
        etablissement.save()
        return etablissement