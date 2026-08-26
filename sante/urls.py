from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('carte/', views.carte, name='carte'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/stats/', views.stats_json, name='stats_json'),
    path('api/etablissements/', views.etablissements_geojson, name='etablissements_geojson'),
    path('api/quartiers/', views.quartiers_geojson, name='quartiers_geojson'),
    path('ajouter/', views.ajouter_etablissement, name='ajouter_etablissement'),
]