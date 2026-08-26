# Carte Sanitaire Interactive — Grand Yoff

Application WebSIG développée dans le cadre du module *Systèmes d'Information Géographique / Développement WebSIG avec Django* (Licence 3 Géomatique, Université Iba Der Thiam de Thiès).

L'application permet de visualiser, rechercher et analyser l'offre de soins de santé de la commune de Grand Yoff (Dakar, Sénégal) : localisation des établissements, indicateur d'accessibilité par quartier, tableau de bord statistique, et contribution citoyenne.

## Fonctionnalités

**Minimales**
- Carte interactive (OpenStreetMap / satellite ESRI)
- Localisation des 51 établissements (postes de santé, centres de santé, hôpitaux, cliniques, pharmacies)
- Fiches d'information (nom, type, quartier)
- Recherche par nom, filtres par type
- Légende dynamique avec compteurs
- Couches administratives (limites des 66 quartiers)

**Bonus**
- Indicateur d'accessibilité (ratio habitants/établissement par quartier, choroplèthe)
- Zones de desserte simplifiées (buffers géométriques à vol d'oiseau, non isochrones)
- Établissement le plus proche (distance à vol d'oiseau via formule de Haversine, géolocalisation navigateur)
- Filtre par secteur public/privé (estimation déduite de la typologie)
- Tableau de bord statistique (répartition par type, classement des quartiers)
- Export des données au format GeoJSON
- Formulaire de contribution citoyenne (ajout d'établissement, géolocalisation automatique)
- Interface responsive (Bootstrap 5)

## Stack technique

| Composant | Technologie |
|---|---|
| Backend | Django + GeoDjango |
| Base de données | PostgreSQL / PostGIS |
| Cartographie | Leaflet.js |
| Graphiques | Chart.js |
| UI | Bootstrap 5 |

## Prérequis

- Python 3.12+
- PostgreSQL 15+ avec extension PostGIS
- GDAL / GEOS (voir note Windows ci-dessous)

## Installation

### 1. Cloner le dépôt
```bash
git clone https://github.com/bunnybugs-bot/carte-sanitaire-grand-dakar.git
cd carte-sanitaire-grand-dakar
```

### 2. Créer un environnement virtuel et installer les dépendances
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Installer et Configurer GDAL (Windows uniquement)
GeoDjango nécessite les bibliothèques GDAL/GEOS. Sous Windows, installez-les via [OSGeo4W](https://trac.osgeo.org/osgeo4w/) (Express Install → cochez GDAL), puis renseignez les chemins dans `config/settings.py` :
```python
import os
os.environ['PATH'] = r'C:\OSGeo4W\bin' + os.pathsep + os.environ['PATH']
GDAL_LIBRARY_PATH = r'C:\OSGeo4W\bin\gdal310.dll'   # adapter le numéro de version slon celle installée
GEOS_LIBRARY_PATH = r'C:\OSGeo4W\bin\geos_c.dll'
```

### 4. Configurer la base de données
Créer une base PostgreSQL avec l'extension PostGIS :
```sql
CREATE DATABASE carte_sanitaire_grand_yoff;
\c carte_sanitaire_grand_yoff
CREATE EXTENSION postgis;
```

Renseigner les identifiants dans `config/settings.py` :
```
python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'carte_sanitaire_grand_yoff',
        'USER': 'postgres',
        'PASSWORD': '<votre_mot_de_passe>',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

> Les tables `etablissement_sante` et `quartier_population` sont importées depuis QGIS (fusion des couches vectorielles) et ne sont pas gérées par les migrations Django (`managed = False`). Voir le Modèle Conceptuel/Physique de Données pour le détail des colonnes.Les couches spatiales (etablissement_sante_test et quartier_population) ont été consolidées et importées sous la référence EPSG:32628 (WGS 84 / UTM zone 28N). Les coordonnées géographiques saisies en WGS84 (EPSG:4326) via le formulaire sont automatiquement reprojetées avant insertion en base.

### 5. Appliquer les migrations et lancer le serveur

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

L'application est accessible sur `http://127.0.0.1:8000/sante/`.

## Structure du projet

carte-sanitaire-grand-yoff/
├── config/                 # Configuration Django (settings, urls globales)
├── sante/                  # Application principale
│   ├── models.py           # Modèles spatiaux (Etablissement, Quartier)
│   ├── admin.py            # Administration géographique
│   ├── views.py            # Vues GeoJSON, filtres, dashboard
│   ├── forms.py            # Formulaire de contribution
│   ├── urls.py              # Routes de l'application
│   ├── templates/sante/    # Templates (accueil, carte, dashboard, formulaire)
│   └── static/sante/img/   # Images et favicon
├── docs/                   # Cahier des charges, MCD/MPD, rapport
└── manage.py

## Sources des données

- Infrastructures de santé : [GeoSénégal](https://www.geosenegal.gouv.sn/senegal-infrastructures-de-sante.html) (hôpitaux, centres et postes de santé), complétées par [OpenStreetMap](https://www.openstreetmap.org/) via QuickOSM (cliniques, pharmacies)
- Population et limites administratives : Agence Nationale de la Statistique et de la Démographie (ANSD)
- Fond de carte : OpenStreetMap, imagerie satellite ESRI

## Limites connues

- Le secteur public/privé est estimé à partir du type d'établissement, non issu d'une donnée vérifiée
- Les zones de desserte sont des buffers géométriques simples (à vol d'oiseau), pas de véritables isochrones piéton/véhicule
- Le calcul « établissement le plus proche » utilise la distance euclidienne, pas un itinéraire routier réel
- Aucune donnée de contact ou de capacité d'accueil disponible pour les établissements

## Équipe

Projet réalisé en groupe par Fatoumata Binta Diallo, Néné Adame Thiam, Abdoulaye Ndao, Dib Marone étudiants — Licence 3 Géomatique, UIDT Thiès.

## Licence

Projet académique — usage pédagogique uniquement. Données tierces soumises à leurs licences respectives (GeoSénégal, OpenStreetMap ODbL, ANSD).
