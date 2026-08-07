#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lit la base Supabase et réécrit data/*.json.

Place dans la chaîne
--------------------
C'est la première étape de la publication (CDC-BACKOFFICE.md § 7). Ensuite
viennent generer-html.py et generer-menu-pdf.py, qui n'ont pas à savoir d'où
viennent les données : leur travail est identique que les fichiers aient été
écrits à la main ou par ce script.

Les règles de traduction vivent dans outils/modele.py, partagées avec
generer-seed-supabase.py et verifier-modele.py. Ce script ne fait que deux
choses : parler à Supabase, et vérifier que le résultat est plausible.

Pourquoi urllib et non le paquet « supabase »
---------------------------------------------
Six requêtes GET sur une API REST ne justifient pas une dépendance. Le reste
de l'outillage du site tient dans la bibliothèque standard ; l'installer dans
GitHub Actions coûterait plus de temps que les requêtes elles-mêmes.

Usage
-----
    export SUPABASE_URL=https://xxxx.supabase.co
    export SUPABASE_SERVICE_KEY=sb_secret_...
    python outils/exporter-supabase.py            # écrit data/*.json
    python outils/exporter-supabase.py --verifier  # compare sans rien écrire

La clé secrète contourne RLS : elle n'a sa place que dans les secrets GitHub
Actions ou dans un shell, jamais dans un fichier du dépôt.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import modele  # noqa: E402

for flux in (sys.stdout, sys.stderr):
    if hasattr(flux, "reconfigure"):
        flux.reconfigure(encoding="utf-8", errors="replace")

TABLES = ("produits", "menus", "menu_lignes", "marches", "avis", "reglages")

# Tables qui ne doivent jamais être exportées, quoi qu'il arrive. « demandes »
# contient des noms, des adresses et des téléphones de clients ; ce script
# écrit dans data/*.json, qui part dans un dépôt GitHub public. L'assertion
# n'est pas décorative : elle fait échouer la publication plutôt que de publier
# le carnet de commandes le jour où quelqu'un ajoutera la table par commodité.
JAMAIS_EXPORTEES = ("demandes",)
assert not set(TABLES) & set(JAMAIS_EXPORTEES), \
    "Une table de données personnelles figure dans TABLES : publication annulée."

# En dessous de ces seuils, on refuse d'écrire. Une base vidée par accident,
# une clé qui ne voit rien à cause de RLS, une table oubliée : sans ce
# garde-fou, la publication remplacerait le site par une coquille vide et
# pousserait le tout sur GitHub sans que personne ne s'en aperçoive.
MINIMUMS = {"produits": 5, "menus": 1, "menu_lignes": 5, "marches": 1, "reglages": 1}


def lire_table(base: str, cle: str, table: str) -> list[dict]:
    requete = urllib.request.Request(
        f"{base}/rest/v1/{table}?select=*",
        headers={"apikey": cle, "Authorization": f"Bearer {cle}",
                 "Accept": "application/json"})
    try:
        with urllib.request.urlopen(requete, timeout=30) as reponse:
            return json.loads(reponse.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:200]
        raise SystemExit(f"Lecture de « {table} » refusée ({e.code}) : {detail}")
    except urllib.error.URLError as e:
        raise SystemExit(f"Supabase injoignable : {e.reason}")


# Les seules colonnes dont la valeur est un nombre. La liste est explicite, et
# c'est volontaire : une normalisation appliquée à l'aveugle transformerait
# « +33627352328 » en entier, et le SIRET « 51134341000037 » avec lui.
COLONNES_NOMBRES = frozenset({
    "prix", "prix_max", "note", "ordre",
    "minimum_parts", "rayon_livraison_km",
    "frais_livraison_proche", "frais_livraison_loin",
})


def normaliser(colonne: str, v):
    """Ramène les nombres à la forme qu'avaient les fichiers d'origine.

    PostgreSQL rend une colonne numeric(6,2) sous la forme 10.00, que Python
    lit comme le flottant 10.0 et réécrit « 10.0 ». Les fichiers d'origine
    portent « 10 ». Sans cette normalisation, chaque prix entier apparaîtrait
    modifié à chaque publication — du bruit qui masquerait les vraies
    modifications, et un échec permanent de la vérification du § 9.
    """
    if colonne not in COLONNES_NOMBRES or v is None or isinstance(v, bool):
        return v
    if isinstance(v, str):
        # Selon la version, PostgREST rend un numeric en nombre ou en chaîne.
        try:
            v = float(v)
        except ValueError:
            return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return v


def recuperer(base: str, cle: str) -> dict:
    brut = {t: lire_table(base, cle, t) for t in TABLES}

    manques = [f"{t} : {len(brut[t])} ligne(s), attendu au moins {n}"
               for t, n in MINIMUMS.items() if len(brut[t]) < n]
    if manques:
        raise SystemExit("La base ne contient pas ce qu'elle devrait — "
                         "rien n'a été écrit.\n  " + "\n  ".join(manques))

    tables = {t: [{c: normaliser(c, v) for c, v in ligne.items()} for ligne in brut[t]]
              for t in TABLES}

    # modele.vers_json rattache les lignes de menu par le slug du menu ; la
    # base, elle, les relie par l'identifiant. On refait le lien ici.
    slug_par_id = {m["id"]: m["slug"] for m in tables["menus"]}
    for ligne in tables["menu_lignes"]:
        ligne["menu_slug"] = slug_par_id.get(ligne["menu_id"])
    orphelines = [l for l in tables["menu_lignes"] if l["menu_slug"] is None]
    if orphelines:
        raise SystemExit(f"{len(orphelines)} ligne(s) de menu ne se rattachent à "
                         "aucun menu — rien n'a été écrit.")

    tables["reglages"] = tables["reglages"][0]
    if not tables["reglages"].get("gabarits"):
        raise SystemExit("Les gabarits sont vides : impossible de reconstituer "
                         "les fichiers. Rien n'a été écrit.")

    return tables


def comparer(documents: dict) -> list[str]:
    """Les fichiers qui changeraient, sans rien écrire."""
    differents = []
    for nom, contenu in documents.items():
        chemin = modele.DATA / f"{nom}.json"
        neuf = json.dumps(contenu, ensure_ascii=False, indent=2) + "\n"
        ancien = chemin.read_text(encoding="utf-8") if chemin.exists() else ""
        if neuf != ancien:
            differents.append(f"{nom}.json")
    return differents


def main() -> int:
    verifier = "--verifier" in sys.argv

    base = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
    cle = os.environ.get("SUPABASE_SERVICE_KEY") or ""
    if not base or not cle:
        raise SystemExit("SUPABASE_URL et SUPABASE_SERVICE_KEY doivent être "
                         "définies dans l'environnement.")

    tables = recuperer(base, cle)
    documents = modele.vers_json(tables)

    print(f"  {len(tables['produits'])} produits · {len(tables['menus'])} menus · "
          f"{len(tables['menu_lignes'])} lignes de menu · "
          f"{len(tables['marches'])} marchés · {len(tables['avis'])} avis")

    differents = comparer(documents)

    if verifier:
        if differents:
            print("\n  Différences : " + ", ".join(differents))
            print("  L'export ne reproduit pas les fichiers actuels.")
            return 1
        print("\n  Aucune différence : l'export est fidèle.")
        return 0

    if not differents:
        print("\n  Aucun changement : les fichiers sont déjà à jour.")
        return 0

    ecrits = modele.ecrire_json(documents)
    print("\n  Réécrits : " + ", ".join(sorted(differents)))
    print(f"  ({len(ecrits)} fichiers examinés)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
