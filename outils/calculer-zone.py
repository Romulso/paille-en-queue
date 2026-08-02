#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recalcule data/zone.json : les communes de la zone de livraison.

Pourquoi
--------
« Jusqu'où vous déplacez-vous ? » est la deuxième question posée au téléphone,
et c'est aussi ce que les gens tapent dans Google : « traiteur » suivi du nom
de leur commune. Une page qui répond précisément, commune par commune, sert
donc autant le client que le référencement.

Les distances sont calculées à vol d'oiseau depuis les coordonnées de
data/config.json, avec les centres officiels des communes fournis par
geo.api.gouv.fr. Rien n'est saisi à la main : le jour où le rayon change dans
config.json, une seule commande suffit.

Usage
-----
    python outils/calculer-zone.py

À relancer si « rayonLivraisonKm » ou les coordonnées changent dans
data/config.json. Nécessite une connexion internet.
"""

from __future__ import annotations

import json
import math
import sys
import urllib.request
from pathlib import Path

for flux in (sys.stdout, sys.stderr):
    if hasattr(flux, "reconfigure"):
        flux.reconfigure(encoding="utf-8", errors="replace")

RACINE = Path(__file__).resolve().parent.parent
DATA = RACINE / "data"

# Départements traversés par le rayon. En ajouter un ici si la zone s'étend.
DEPARTEMENTS = ["24", "33"]

API = ("https://geo.api.gouv.fr/communes?codeDepartement={}"
       "&fields=nom,centre,population,codesPostaux&format=json")

# On garde toutes les communes proches, et au-delà seulement celles qui sont
# assez peuplées pour qu'on les cherche : sinon la page devient un annuaire
# illisible de 433 lignes, ce que Google n'aime pas plus que le lecteur.
PROCHE_KM = 12
POPULATION_MINIMALE = 900


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    rayon_terre = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2)
    return rayon_terre * 2 * math.asin(math.sqrt(a))


def main() -> int:
    cfg = json.loads((DATA / "config.json").read_text(encoding="utf-8"))
    if not (cfg.get("latitude") and cfg.get("longitude")):
        sys.exit("Coordonnées absentes de data/config.json (admin.html → Réglages).")

    lat, lon = float(cfg["latitude"]), float(cfg["longitude"])
    rayon = cfg["rayonLivraisonKm"]

    retenues, total, population = [], 0, 0
    for departement in DEPARTEMENTS:
        print(f"  département {departement}…")
        with urllib.request.urlopen(API.format(departement), timeout=30) as r:
            communes = json.load(r)
        for commune in communes:
            lon_c, lat_c = commune["centre"]["coordinates"]
            km = distance_km(lat, lon, lat_c, lon_c)
            if km > rayon:
                continue
            habitants = commune.get("population") or 0
            total += 1
            population += habitants
            if km <= PROCHE_KM or habitants >= POPULATION_MINIMALE:
                retenues.append({
                    "nom": commune["nom"],
                    "cp": commune["codesPostaux"][0],
                    "km": round(km),
                    "pop": habitants,
                    "dep": departement,
                })

    retenues.sort(key=lambda c: (c["km"], c["nom"]))
    sortie = {
        "_lisezmoi": (
            "Communes de la zone de livraison, calculées depuis les coordonnées de "
            "data/config.json avec les données officielles de geo.api.gouv.fr "
            "(centre de chaque commune, distance à vol d'oiseau). Régénéré par "
            "outils/calculer-zone.py — ne pas modifier à la main."),
        "origine": {"latitude": lat, "longitude": lon},
        "rayonKm": rayon,
        "totalCommunes": total,
        "populationCouverte": population,
        "communes": retenues,
    }
    (DATA / "zone.json").write_text(
        json.dumps(sortie, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8", newline="\n")

    print(f"{total} communes dans le rayon de {rayon} km, "
          f"{population} habitants.")
    print(f"{len(retenues)} communes retenues pour la page.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
