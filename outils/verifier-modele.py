#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prouve que le modèle relationnel ne perd aucune information.

Le principe
-----------
On prend les fichiers data/*.json, on les éclate en lignes de tables, on les
reconstitue, et on compare au caractère près avec les originaux. Si les deux
sont identiques, le passage par Supabase est neutre : c'est exactement la
garantie que demande CDC-BACKOFFICE.md § 9.

Tout se fait en mémoire, sans base de données et sans réseau. Le test peut
donc tourner avant même que le projet Supabase existe — c'est tout l'intérêt :
il valide le schéma avant qu'on ait passé une soirée à le remplir.

Ce qu'il attrape
----------------
Les pertes silencieuses : une clé de documentation oubliée, un ordre de clés
qui change, un « vedette: false » ajouté là où le fichier d'origine n'avait
rien, un « jusquau » vide devenu null. Aucune de ces différences ne casse le
site, mais chacune fait apparaître les fichiers comme modifiés à chaque
publication — et noie les vraies modifications dans le bruit.

Usage
-----
    python outils/verifier-modele.py

Sort en code 0 si le modèle est fidèle, 1 sinon.
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


def comparer(nom: str, avant, apres, chemin: str = "") -> list[str]:
    """Compare deux documents et décrit les différences en français.

    L'ordre des clés compte : deux dictionnaires égaux au sens de Python
    peuvent produire deux fichiers différents.
    """
    ecarts = []
    ou = f"{nom}{chemin}"

    if type(avant) is not type(apres):
        return [f"{ou} : type {type(avant).__name__} devenu {type(apres).__name__}"]

    if isinstance(avant, dict):
        if list(avant) != list(apres):
            manquantes = [c for c in avant if c not in apres]
            ajoutees = [c for c in apres if c not in avant]
            if manquantes:
                ecarts.append(f"{ou} : clés perdues → {', '.join(manquantes)}")
            if ajoutees:
                ecarts.append(f"{ou} : clés ajoutées → {', '.join(ajoutees)}")
            if not manquantes and not ajoutees:
                ecarts.append(f"{ou} : mêmes clés, ordre différent\n"
                              f"      avant : {', '.join(list(avant))}\n"
                              f"      après : {', '.join(list(apres))}")
        for cle in avant:
            if cle in apres:
                ecarts += comparer(nom, avant[cle], apres[cle], f"{chemin}.{cle}")
        return ecarts

    if isinstance(avant, list):
        if len(avant) != len(apres):
            return [f"{ou} : {len(avant)} éléments devenus {len(apres)}"]
        for i, (a, b) in enumerate(zip(avant, apres)):
            ecarts += comparer(nom, a, b, f"{chemin}[{i}]")
        return ecarts

    if avant != apres:
        ecarts.append(f"{ou} : {json.dumps(avant, ensure_ascii=False)} "
                      f"→ {json.dumps(apres, ensure_ascii=False)}")
    return ecarts


def main() -> int:
    originaux = {nom: modele.lire(nom)
                 for nom in ("carte", "marches", "avis", "config")}

    tables = modele.vers_tables(originaux["carte"], originaux["marches"],
                                originaux["avis"], originaux["config"])
    reconstitues = modele.vers_json(tables)

    print("Aller-retour  data/*.json → tables → data/*.json\n")
    print(f"  {len(tables['produits'])} produits · {len(tables['menus'])} menus · "
          f"{len(tables['menu_lignes'])} lignes de menu · "
          f"{len(tables['marches'])} marchés · {len(tables['avis'])} avis\n")

    total = 0
    for nom, avant in originaux.items():
        ecarts = comparer(f"{nom}.json", avant, reconstitues[nom])
        # La comparaison structurelle ne suffit pas : deux documents identiques
        # peuvent s'écrire différemment. On compare aussi le texte produit.
        texte_avant = json.dumps(avant, ensure_ascii=False, indent=2)
        texte_apres = json.dumps(reconstitues[nom], ensure_ascii=False, indent=2)
        if not ecarts and texte_avant != texte_apres:
            ecarts = [f"{nom}.json : structures égales mais textes différents"]

        if ecarts:
            total += len(ecarts)
            print(f"  ✗ {nom}.json")
            for e in ecarts:
                print(f"      {e}")
        else:
            print(f"  ✓ {nom}.json — identique")

    print()
    if total:
        print(f"{total} différence(s) : le modèle perd de l'information.")
        print("Corriger outils/modele.py, puis relancer.")
        return 1

    print("Aucune différence : le passage par la base est neutre.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
