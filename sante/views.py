from django.core.serializers import serialize
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count
from .models import Etablissement, Quartier
from django.shortcuts import render, redirect
from .forms import EtablissementForm

def accueil(request):
    context = {
        'nb_etablissements': Etablissement.objects.count(),
        'nb_types': Etablissement.objects.values('amenity').distinct().count(),
        'nb_quartiers': Quartier.objects.count(),
        'etablissements_urgence': [
            {'nom': 'Hôpital Idrissa Pouye (ex-HOGGY)', 'type': 'Hôpital public', 'quartier': 'Zone de captage', 'telephone': '33 869 40 50'},
            {'nom': 'CS SAMU Municipal', 'type': 'Centre de santé', 'quartier': 'Sud Foire', 'telephone': '33 827 27 72'},
            {'nom': 'CENTRE DE BOPP', 'type': 'Centre de santé', 'quartier': 'Bopp', 'telephone': '33 825 39 77'},
        ],
    }
    return render(request, 'sante/home.html', context)


def dashboard(request):
    return render(request, 'sante/dashboard.html')


def stats_json(request):
    par_type = list(
        Etablissement.objects.values('amenity').annotate(total=Count('id')).order_by('-total')
    )
    top_quartiers = list(
        Etablissement.objects.exclude(quartier__isnull=True)
        .values('quartier').annotate(total=Count('id')).order_by('-total')[:10]
    )

    # Quartiers les moins bien desservis (ratio habitants/établissement le plus élevé)
    accessibilite = []
    for q in Quartier.objects.exclude(population__isnull=True):
        nb = Etablissement.objects.filter(quartier__iexact=q.qrt_vlg_ha).count()
        if nb > 0 and q.population:
            accessibilite.append({
                'quartier': q.qrt_vlg_ha,
                'population': q.population,
                'nb': nb,
                'ratio': round(q.population / nb),
            })
    accessibilite = sorted(accessibilite, key=lambda x: -x['ratio'])[:10]

    return JsonResponse({
        'par_type': par_type,
        'top_quartiers': top_quartiers,
        'accessibilite': accessibilite,
        'nb_etablissements': Etablissement.objects.count(),
        'nb_types': Etablissement.objects.values('amenity').distinct().count(),
        'nb_quartiers': Quartier.objects.count(),
        'type_dominant': par_type[0]['amenity'] if par_type else '—',
    })

def etablissements_geojson(request):
    etablissements = Etablissement.objects.filter(geom__isnull=False)
    
        # Filtre par type d'établissement (ex: ?type=Pharmacie)
    type_param = request.GET.get('type')
    if type_param:
        etablissements = etablissements.filter(amenity=type_param)

    # Recherche par nom (ex: ?q=sonatel)
    search_param = request.GET.get('q')
    if search_param:
        etablissements = etablissements.filter(name__icontains=search_param)

    # Filtre par quartier (ex: ?quartier=ZONE DE CAPTAGE)
    quartier_param = request.GET.get('quartier')
    if quartier_param:
        etablissements = etablissements.filter(quartier__icontains=quartier_param)
    
    geojson = serialize('geojson', etablissements, geometry_field='geom', fields=('name', 'amenity', 'quartier'))
    return HttpResponse(geojson, content_type='application/json')


def quartiers_geojson(request):
    quartiers = Quartier.objects.all()
    geojson = serialize('geojson', quartiers, geometry_field='geom', fields=('qrt_vlg_ha', 'population', 'ccrca'))
    return HttpResponse(geojson, content_type='application/json')

from django.contrib import messages

def ajouter_etablissement(request):
    if request.method == 'POST':
        form = EtablissementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Établissement ajouté avec succès !")
            return redirect('ajouter_etablissement')
    else:
        form = EtablissementForm()
    return render(request, 'sante/ajouter_etablissement.html', {'form': form})

def carte(request):
    return render(request, 'sante/carte.html')