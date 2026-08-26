from django.contrib.gis import admin
from .models import Etablissement, Quartier


@admin.register(Etablissement)
class EtablissementAdmin(admin.GISModelAdmin):
    list_display = ('name', 'amenity', 'quartier')
    list_filter = ('amenity',)
    search_fields = ('name', 'quartier')


@admin.register(Quartier)
class QuartierAdmin(admin.GISModelAdmin):
    list_display = ('qrt_vlg_ha', 'population', 'ccrca')
    search_fields = ('qrt_vlg_ha',)