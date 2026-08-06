#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transforme data/*.json en SQL d'import pour Supabase.

Pourquoi un script plutôt qu'un copier-coller
---------------------------------------------
L'import initial n'a lieu qu'une fois, mais on le rejouera : à chaque
correction du schéma, à chaque base de test créée, à chaque reprise à zéro.
Le refaire à la main, c'est réintroduire une faute de frappe à chaque fois.

Les règles de traduction vivent dans outils/modele.py, partagées avec
verifier-modele.py et, plus tard, exporter-supabase.py. Ce script ne fait que
mettre en forme du SQL.

Usage
-----
    python outils/generer-seed-supabase.py

Puis coller supabase/donnees-initiales.sql dans l'éditeur SQL de Supabase,
après supabase/schema.sql. Le fichier produit est ré-exécutable : il vide les
tables avant de les remplir.

Aucune dépendance : bibliothèque standard seulement.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import modele  # noqa: E402

for flux in (sys.stdout, sys.stderr):
    if hasattr(flux, "reconfigure"):
        flux.reconfigure(encoding="utf-8", errors="replace")

SORTIE = modele.RACINE / "supabase" / "donnees-initiales.sql"


# --------------------------------------------------------------------------
# Écriture des valeurs SQL
# --------------------------------------------------------------------------

def valeur(v) -> str:
    """Une valeur Python écrite en littéral SQL.

    Le seul échappement nécessaire dans du texte est le doublement des
    apostrophes — et il y en a partout dans les descriptions créoles
    (« jusqu'à ce que », « l'océan Indien »).
    """
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def json_sql(v) -> str:
    """Un objet JSON destiné à une colonne « json ».

    ensure_ascii=False garde les accents lisibles dans le fichier SQL, et on
    ne trie surtout pas les clés : leur ordre est précisément ce que le
    gabarit est chargé de préserver.
    """
    return valeur(json.dumps(v, ensure_ascii=False, indent=2)) + "::json"


def insertion(table: str, colonnes: list[str], lignes: list[dict],
              transformer=None) -> list[str]:
    """Un « insert » multi-lignes, une ligne de SQL par enregistrement."""
    if not lignes:
        return [f"-- Aucune donnée pour {table}."]
    rendu = transformer or (lambda l: [valeur(l[c]) for c in colonnes])
    corps = ",\n".join("  (" + ", ".join(rendu(l)) + ")" for l in lignes)
    return [f"insert into {table} ({', '.join(colonnes)}) values", corps + ";"]


# --------------------------------------------------------------------------

def construire() -> str:
    tables = modele.vers_tables(
        modele.lire("carte"), modele.lire("marches"),
        modele.lire("avis"), modele.lire("config"))

    cols_produits = ["famille", "slug", "nom", "description", "prix", "unite",
                     "categorie", "vedette", "ordre", "actif"]
    cols_menus = ["slug", "nom", "resume", "prix", "prix_max",
                  "supplement_motif", "ordre", "actif"]
    cols_marches = ["lieu", "jour", "type", "horaire", "details", "jusquau",
                    "ordre", "actif"]
    cols_avis = ["auteur", "note", "contexte", "texte", "publie", "ordre"]

    # Les lignes de menu se rattachent par le slug du menu et non par un
    # identifiant : les uuid sont engendrés par la base, on ne les connaît pas
    # à l'écriture du fichier. Un sous-select fait le lien à l'exécution.
    def ligne_menu(l):
        return [f"(select id from menus where slug = {valeur(l['menu_slug'])})",
                valeur(l["bloc"]), valeur(l["libelle"]), valeur(l["ordre"])]

    reglages = tables["reglages"]
    cols_reglages = [c for c in reglages if c != "gabarits"] + ["gabarits"]

    def ligne_reglages(l):
        return [json_sql(l["gabarits"]) if c == "gabarits" else valeur(l[c])
                for c in cols_reglages]

    bloc = [
        "-- " + "=" * 74,
        "-- Le Paille en Queue — données initiales",
        "-- " + "=" * 74,
        "--",
        "-- Fichier ENGENDRÉ par outils/generer-seed-supabase.py.",
        "-- Ne pas le modifier à la main : modifier data/*.json et relancer.",
        "--",
        "-- À exécuter dans l'éditeur SQL de Supabase, après schema.sql.",
        "-- Ré-exécutable : les tables sont vidées avant remplissage.",
        "-- " + "=" * 74,
        "",
        "-- « cascade » vide aussi menu_lignes, qui référence menus.",
        "truncate menu_lignes, menus, produits, marches, avis, reglages cascade;",
        "",
        "-- " + "-" * 74,
        f"-- Produits ({len(tables['produits'])})",
        "-- " + "-" * 74,
        *insertion("produits", cols_produits, tables["produits"]),
        "",
        "-- " + "-" * 74,
        f"-- Menus ({len(tables['menus'])}) et leur composition "
        f"({len(tables['menu_lignes'])} lignes)",
        "-- " + "-" * 74,
        *insertion("menus", cols_menus, tables["menus"]),
        "",
        *insertion("menu_lignes", ["menu_id", "bloc", "libelle", "ordre"],
                   tables["menu_lignes"], ligne_menu),
        "",
        "-- " + "-" * 74,
        f"-- Marchés ({len(tables['marches'])})",
        "-- " + "-" * 74,
        *insertion("marches", cols_marches, tables["marches"]),
        "",
        "-- " + "-" * 74,
        f"-- Avis ({len(tables['avis'])})",
        "-- " + "-" * 74,
        *insertion("avis", cols_avis, tables["avis"]),
        "",
        "-- " + "-" * 74,
        "-- Réglages — ligne unique, gabarits compris",
        "-- " + "-" * 74,
        *insertion("reglages", cols_reglages, [reglages], ligne_reglages),
        "",
        "-- " + "-" * 74,
        "-- Contrôle : les comptes attendus",
        "-- " + "-" * 74,
        f"--   produits {len(tables['produits'])} · menus {len(tables['menus'])} · "
        f"lignes de menu {len(tables['menu_lignes'])} · "
        f"marchés {len(tables['marches'])} · avis {len(tables['avis'])}",
        "--",
        "--   select 'produits' t, count(*) from produits",
        "--   union all select 'menus', count(*) from menus",
        "--   union all select 'menu_lignes', count(*) from menu_lignes",
        "--   union all select 'marches', count(*) from marches",
        "--   union all select 'avis', count(*) from avis",
        "--   union all select 'reglages', count(*) from reglages;",
        "",
    ]
    return "\n".join(bloc) + "\n"


if __name__ == "__main__":
    SORTIE.parent.mkdir(exist_ok=True)
    SORTIE.write_text(construire(), encoding="utf-8", newline="\n")

    tables = modele.vers_tables(
        modele.lire("carte"), modele.lire("marches"),
        modele.lire("avis"), modele.lire("config"))
    print(f"  ✓ {SORTIE.relative_to(modele.RACINE)}  "
          f"{SORTIE.stat().st_size / 1024:.0f} Ko")
    print(f"    {len(tables['produits'])} produits · {len(tables['menus'])} menus · "
          f"{len(tables['menu_lignes'])} lignes de menu · "
          f"{len(tables['marches'])} marchés · {len(tables['avis'])} avis")
