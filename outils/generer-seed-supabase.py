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

def texte_sql(s: str) -> str:
    """Une chaîne SQL, garantie en pur ASCII.

    Pourquoi ne pas simplement écrire les accents
    ---------------------------------------------
    Ce fichier est destiné à être collé dans l'éditeur SQL de Supabase, et ce
    trajet passe par le presse-papiers puis par le navigateur. On a constaté
    qu'il pouvait réinterpréter l'UTF-8 en MacRoman en chemin : « Réunion »
    arrive alors en base sous la forme « R√©union », sans la moindre erreur
    pour le signaler.

    Un fichier en pur ASCII est immunisé : aucune conversion d'encodage ne
    peut l'abîmer. Les caractères accentués sont écrits en échappements
    \\uXXXX dans une chaîne E'…', que PostgreSQL décode lui-même.

    Le doublement des apostrophes reste nécessaire : il y en a partout dans
    les descriptions créoles (« jusqu'à ce que », « l'océan Indien »).
    """
    if s.isascii():
        return "'" + s.replace("'", "''") + "'"

    morceaux = []
    for c in s:
        point = ord(c)
        if c == "'":
            morceaux.append("''")
        elif c == "\\":
            morceaux.append("\\\\")
        elif point < 128:
            morceaux.append(c)
        elif point <= 0xFFFF:
            morceaux.append(f"\\u{point:04x}")
        else:
            morceaux.append(f"\\U{point:08x}")
    return "E'" + "".join(morceaux) + "'"


def valeur(v) -> str:
    """Une valeur Python écrite en littéral SQL."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    return texte_sql(str(v))


def json_sql(v) -> str:
    """Un objet JSON destiné à une colonne « json ».

    ensure_ascii=True fait écrire les accents en \\uXXXX par la bibliothèque
    JSON elle-même : le littéral reste en ASCII pour la même raison que
    ci-dessus, et PostgreSQL conserve ce texte tel quel — le type « json » ne
    normalise pas. Les clés ne sont surtout pas triées : leur ordre est
    précisément ce que le gabarit est chargé de préserver.
    """
    return texte_sql(json.dumps(v, ensure_ascii=True, indent=2)) + "::json"


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

    # Les commentaires eux-mêmes sont sans accents, volontairement : affichés
    # abîmés dans l'éditeur Supabase, ils feraient douter de l'intégrité des
    # données alors que celles-ci sont protégées par les échappements \uXXXX.
    bloc = [
        "-- " + "=" * 74,
        "-- Le Paille en Queue - import initial",
        "-- " + "=" * 74,
        "--",
        "-- Fichier engendre par outils/generer-seed-supabase.py.",
        "-- Ne pas le modifier a la main : modifier data/*.json et relancer.",
        "--",
        "-- A executer dans l'editeur SQL de Supabase, apres schema.sql.",
        "-- Re-executable : les tables sont videes avant remplissage.",
        "--",
        "-- Ce fichier est en pur ASCII, commentaires compris. Le trajet",
        "-- presse-papiers puis navigateur peut reinterpreter l'UTF-8 en chemin,",
        "-- et \"Reunion\" arriverait en base abime, sans erreur pour le dire.",
        "-- Les accents sont donc ecrits en \\uXXXX et decodes par PostgreSQL.",
        "-- " + "=" * 74,
        "",
        "-- \"cascade\" vide aussi menu_lignes, qui reference menus.",
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
        f"-- Marches ({len(tables['marches'])})",
        "-- " + "-" * 74,
        *insertion("marches", cols_marches, tables["marches"]),
        "",
        "-- " + "-" * 74,
        f"-- Avis ({len(tables['avis'])})",
        "-- " + "-" * 74,
        *insertion("avis", cols_avis, tables["avis"]),
        "",
        "-- " + "-" * 74,
        "-- Reglages - ligne unique, gabarits compris",
        "-- " + "-" * 74,
        *insertion("reglages", cols_reglages, [reglages], ligne_reglages),
        "",
        "-- " + "-" * 74,
        "-- Controle : les comptes attendus",
        "-- " + "-" * 74,
        f"--   produits {len(tables['produits'])} | menus {len(tables['menus'])} | "
        f"lignes de menu {len(tables['menu_lignes'])} | "
        f"marches {len(tables['marches'])} | avis {len(tables['avis'])}",
        "--",
        "--   select 'produits' t, count(*) from produits",
        "--   union all select 'menus', count(*) from menus",
        "--   union all select 'menu_lignes', count(*) from menu_lignes",
        "--   union all select 'marches', count(*) from marches",
        "--   union all select 'avis', count(*) from avis",
        "--   union all select 'reglages', count(*) from reglages;",
        "",
    ]
    sql = "\n".join(bloc) + "\n"

    # Garde-fou : le fichier ne doit jamais contenir un octet non ASCII. Si
    # cette exception se déclenche, c'est qu'un chemin d'écriture a été ajouté
    # sans passer par texte_sql(), et les accents repartiraient sans protection.
    if not sql.isascii():
        fautifs = [l for l in sql.splitlines() if not l.isascii()][:3]
        raise SystemExit("Le SQL engendré n'est pas en pur ASCII :\n  "
                         + "\n  ".join(fautifs))
    return sql


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
