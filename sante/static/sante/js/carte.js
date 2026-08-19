/* ===========================================================
   carte.js — Interface cartographique (Personne 4)
   Consomme les vues GeoJSON exposées par Personne 3 :
     - URL_ETABLISSEMENTS_GEOJSON
     - URL_QUARTIERS_GEOJSON
     - URL_COMMUNE_GEOJSON
   =========================================================== */

document.addEventListener("DOMContentLoaded", function () {

    /* ---------- 1. Initialisation de la carte ---------- */
    const map = L.map("carte", {
        zoomControl: true
    }).setView([14.6928, -17.4467], 12); // vue par défaut, à ajuster à la commune

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
        maxZoom: 19
    }).addTo(map);

    /* ---------- 2. Styles par type d'établissement ---------- */
    const COULEURS_TYPE = {
        hopital: "#d63384",
        centre_sante: "#0d6efd",
        poste_sante: "#198754",
        clinique: "#fd7e14",
        pharmacie: "#6f42c1"
    };

    const LABELS_TYPE = {
        hopital: "Hôpital",
        centre_sante: "Centre de santé",
        poste_sante: "Poste de santé",
        clinique: "Clinique",
        pharmacie: "Pharmacie"
    };

    function creerMarqueur(feature, latlng) {
        const type = feature.properties.type;
        const couleur = COULEURS_TYPE[type] || "#6c757d";
        return L.circleMarker(latlng, {
            radius: 8,
            fillColor: couleur,
            color: "#212529",
            weight: 1,
            opacity: 1,
            fillOpacity: 0.9
        });
    }

    /* ---------- 3. Couches ---------- */
    let coucheEtablissements = null;   // L.geoJSON des établissements (avec filtrage)
    let donneesEtablissements = null;  // FeatureCollection brute
    let coucheQuartiers = null;
    let coucheCommune = null;

    function contenuPopup(props) {
        return `
            <div>
                <h6>${props.nom}</h6>
                <span class="badge" style="background:${COULEURS_TYPE[props.type] || '#6c757d'}">
                    ${LABELS_TYPE[props.type] || props.type}
                </span>
                <span class="badge bg-secondary">${props.statut || ""}</span>
                <div class="popup-btn">
                    <button class="btn btn-sm btn-primary btn-voir-fiche" data-id="${props.id}">
                        Voir la fiche
                    </button>
                </div>
            </div>
        `;
    }

    function chargerEtablissements() {
        fetch(URL_ETABLISSEMENTS_GEOJSON)
            .then(res => res.json())
            .then(geojson => {
                donneesEtablissements = geojson;
                afficherEtablissements(geojson);
            })
            .catch(err => console.error("Erreur de chargement des établissements :", err));
    }

    function afficherEtablissements(geojson) {
        if (coucheEtablissements) {
            map.removeLayer(coucheEtablissements);
        }
        coucheEtablissements = L.geoJSON(geojson, {
            pointToLayer: creerMarqueur,
            onEachFeature: function (feature, layer) {
                layer.bindPopup(contenuPopup(feature.properties));
                layer.on("popupopen", function () {
                    const btn = document.querySelector(".btn-voir-fiche");
                    if (btn) {
                        btn.addEventListener("click", function () {
                            afficherFicheEtablissement(feature.properties);
                        });
                    }
                });
            }
        }).addTo(map);

        document.getElementById("compteurResultats").textContent =
            geojson.features.length + " établissement(s) affiché(s)";
    }

    function chargerQuartiers() {
        fetch(URL_QUARTIERS_GEOJSON)
            .then(res => res.json())
            .then(geojson => {
                coucheQuartiers = L.geoJSON(geojson, {
                    style: { color: "#6c757d", weight: 2, dashArray: "4,4", fillOpacity: 0.03 }
                }).addTo(map);
            })
            .catch(err => console.warn("Couche quartiers indisponible :", err));
    }

    function chargerCommune() {
        fetch(URL_COMMUNE_GEOJSON)
            .then(res => res.json())
            .then(geojson => {
                coucheCommune = L.geoJSON(geojson, {
                    style: { color: "#212529", weight: 3, fillOpacity: 0 }
                }).addTo(map);
                if (coucheCommune.getBounds().isValid()) {
                    map.fitBounds(coucheCommune.getBounds());
                }
            })
            .catch(err => console.warn("Couche commune indisponible :", err));
    }

    chargerEtablissements();
    chargerQuartiers();
    chargerCommune();

    /* ---------- 4. Fiche établissement (offcanvas) ---------- */
    const offcanvasFiche = new bootstrap.Offcanvas(document.getElementById("ficheEtablissement"));

    function afficherFicheEtablissement(props) {
        document.getElementById("ficheNom").textContent = props.nom || "Établissement";
        document.getElementById("ficheType").textContent = LABELS_TYPE[props.type] || props.type || "";
        document.getElementById("ficheStatut").textContent = props.statut || "";
        document.getElementById("ficheSecteur").textContent = props.secteur || "-";
        document.getElementById("ficheContact").textContent = props.contact || "-";
        document.getElementById("ficheCapacite").textContent = props.capacite || "-";
        document.getElementById("ficheQuartier").textContent = props.quartier || "-";
        document.getElementById("ficheAdresse").textContent = props.adresse || "-";
        document.getElementById("ficheDescription").textContent = props.description || "";

        if (props.latitude && props.longitude) {
            document.getElementById("ficheItineraire").href =
                `https://www.google.com/maps/dir/?api=1&destination=${props.latitude},${props.longitude}`;
        }

        offcanvasFiche.show();
    }

    /* ---------- 5. Filtres et recherche ---------- */
    function appliquerFiltres() {
        if (!donneesEtablissements) return;

        const texte = document.getElementById("filtreRecherche").value.trim().toLowerCase();
        const type = document.getElementById("filtreType").value;
        const statut = document.getElementById("filtreStatut").value;
        const secteursActifs = Array.from(document.querySelectorAll(".filtreSecteur:checked"))
            .map(cb => cb.value);

        const featuresFiltres = donneesEtablissements.features.filter(f => {
            const p = f.properties;
            const matchTexte = !texte || (p.nom && p.nom.toLowerCase().includes(texte));
            const matchType = !type || p.type === type;
            const matchStatut = !statut || p.statut === statut;
            const matchSecteur = !p.secteur || secteursActifs.includes(p.secteur);
            return matchTexte && matchType && matchStatut && matchSecteur;
        });

        afficherEtablissements({ type: "FeatureCollection", features: featuresFiltres });
    }

    document.getElementById("filtreRecherche").addEventListener("input", appliquerFiltres);
    document.getElementById("filtreType").addEventListener("change", appliquerFiltres);
    document.getElementById("filtreStatut").addEventListener("change", appliquerFiltres);
    document.querySelectorAll(".filtreSecteur").forEach(cb =>
        cb.addEventListener("change", appliquerFiltres)
    );

    document.getElementById("btnReinitialiser").addEventListener("click", function () {
        document.getElementById("filtreRecherche").value = "";
        document.getElementById("filtreType").value = "";
        document.getElementById("filtreStatut").value = "";
        document.querySelectorAll(".filtreSecteur").forEach(cb => cb.checked = true);
        if (donneesEtablissements) afficherEtablissements(donneesEtablissements);
    });

    /* ---------- 6. Bascule des couches administratives ---------- */
    document.getElementById("toggleCommune").addEventListener("change", function (e) {
        if (!coucheCommune) return;
        if (e.target.checked) map.addLayer(coucheCommune);
        else map.removeLayer(coucheCommune);
    });

    document.getElementById("toggleQuartiers").addEventListener("change", function (e) {
        if (!coucheQuartiers) return;
        if (e.target.checked) map.addLayer(coucheQuartiers);
        else map.removeLayer(coucheQuartiers);
    });

    /* ---------- 7. Contribution citoyenne : clic sur la carte ---------- */
    let marqueurContribution = null;

    map.on("click", function (e) {
        const modalOuvert = document.querySelector("#modalContribution.show");
        if (!modalOuvert) return; // on ne place le point que si le formulaire est ouvert

        if (marqueurContribution) map.removeLayer(marqueurContribution);
        marqueurContribution = L.marker(e.latlng).addTo(map);

        document.getElementById("idLatitude").value = e.latlng.lat;
        document.getElementById("idLongitude").value = e.latlng.lng;
    });

});
