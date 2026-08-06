# -*- coding: utf-8 -*-
"""
Traduction entre data/*.json et le modèle relationnel du backoffice.

Pourquoi ce module existe
-------------------------
Trois scripts ont besoin exactement des mêmes règles de traduction :

- generer-seed-supabase.py  : JSON → tables, pour l'import initial ;
- verifier-modele.py        : JSON → tables → JSON, pour prouver la fidélité ;
- exporter-supabase.py      : tables → JSON, à chaque publication (phase 3).

Les écrire trois fois, c'est garantir qu'elles finiront par diverger — et une
divergence ici se traduit par une carte fausse sur le site.

Le gabarit
----------
Le cahier des charges demande (§ 9) que « generer-html.py ne produise aucune
différence après export ». C'est plus exigeant qu'il n'y paraît : les fichiers
JSON contiennent des clés de documentation (« _lisezmoi », « _supplements »)
intercalées entre les données, et leur ordre est voulu. Une base de données
n'a aucune notion d'ordre des clés.

D'où le gabarit : on stocke chaque fichier JSON tel quel, en remplaçant les
seules parties pilotées par la base par un repère (« @produits:plat »). À
l'export, on parcourt le gabarit et on remplace les repères par les données
fraîches. L'ordre, les commentaires et la forme sont conservés par
construction, sans qu'aucun script n'ait à les connaître.
"""

from __future__ import annotations

import json
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DATA = RACINE / "data"

# Champs de config.json promus en colonnes de la table reglages (CDC § 4).
# Tout le reste demeure dans le gabarit, à sa place et dans l'ordre.
COLONNES_REGLAGES = {
    "telephone": "telephone",
    "telephoneLien": "telephone_lien",
    "email": "email",
    "villeAffichee": "ville_affichee",
    "minimumParts": "minimum_parts",
    "fraisLivraisonProche": "frais_livraison_proche",
    "fraisLivraisonLoin": "frais_livraison_loin",
    "rayonLivraisonKm": "rayon_livraison_km",
    "facebook": "facebook",
    "instagram": "instagram",
    "googleBusinessProfile": "google_business_profile",
    "avisGoogleNote": "avis_google_note",
    "avisGoogleNombre": "avis_google_nombre",
    "avisFacebookTaux": "avis_facebook_taux",
    "avisFacebookNombre": "avis_facebook_nombre",
    "abonnesFacebook": "abonnes_facebook",
}

# Nom de la liste dans carte.json ↔ valeur de la colonne « famille ».
FAMILLES = (("plats", "plat"), ("entrees", "entree"),
            ("boissons", "boisson"), ("supplements", "supplement"))

BLOCS_MENU = (("entree", "entree"), ("plat", "plats"),
              ("dessert", "dessert"), ("inclus", "inclus"))


def lire(nom: str) -> dict:
    with (DATA / f"{nom}.json").open(encoding="utf-8") as f:
        return json.load(f)


# ==========================================================================
# JSON → tables
# ==========================================================================

def vers_tables(carte: dict, marches: dict, avis: dict, cfg: dict) -> dict:
    """Les quatre fichiers JSON, éclatés en lignes de tables.

    Renvoie un dictionnaire dont les clés portent le nom des tables. L'ordre
    d'affichage sur le site est conservé dans la colonne « ordre » : c'est la
    seule chose qu'une table, non ordonnée par nature, ne saurait retrouver.
    """
    produits = []
    for cle, famille in FAMILLES:
        for i, p in enumerate(carte[cle]):
            produits.append({
                "famille": famille,
                "slug": p["slug"],
                "nom": p["nom"],
                "description": p["description"],
                "prix": p.get("prix"),
                "unite": p.get("unite"),
                "categorie": p.get("categorie"),
                "vedette": bool(p.get("vedette")),
                "ordre": i,
                "actif": True,
            })

    menus, menu_lignes = [], []
    for i, m in enumerate(carte["menus"]):
        menus.append({
            "slug": m["slug"],
            "nom": m["nom"],
            "resume": m.get("resume", ""),
            "prix": m["prix"],
            "prix_max": m.get("prixMax"),
            "supplement_motif": m.get("supplementMotif"),
            "ordre": i,
            "actif": True,
        })
        for bloc, cle in BLOCS_MENU:
            for j, libelle in enumerate(m.get(cle) or []):
                menu_lignes.append({"menu_slug": m["slug"], "bloc": bloc,
                                    "libelle": libelle, "ordre": j})

    lignes_marches = [{
        "lieu": m["lieu"],
        "jour": m["jour"],
        "type": m.get("type", "matin"),
        "horaire": m.get("horaire", ""),
        # « precision » est un mot-clé SQL : la colonne s'appelle « details ».
        "details": m.get("precision", ""),
        # Le JSON écrit "" quand il n'y a pas de fin de saison ; la base écrit
        # null. Le gabarit refera le chemin inverse à l'export.
        "jusquau": m.get("jusquau") or None,
        "ordre": i,
        "actif": True,
    } for i, m in enumerate(marches["marches"])]

    lignes_avis = [{
        "auteur": a["auteur"],
        "note": a["note"],
        "contexte": a.get("contexte", ""),
        "texte": a["texte"],
        # Tout avis déjà présent dans le fichier est, par définition, publié.
        "publie": True,
        "ordre": i,
    } for i, a in enumerate(avis["avis"])]

    reglages = {colonne: cfg[cle] for cle, colonne in COLONNES_REGLAGES.items()}
    reglages["gabarits"] = gabarits(carte, marches, avis, cfg)

    return {"produits": produits, "menus": menus, "menu_lignes": menu_lignes,
            "marches": lignes_marches, "avis": lignes_avis, "reglages": reglages}


def gabarits(carte: dict, marches: dict, avis: dict, cfg: dict) -> dict:
    """Les quatre fichiers, vidés de ce que la base sait reconstituer.

    Ce qui reste : les clés de documentation, les mentions commerciales, le
    bloc buffet, les réglages techniques — et surtout l'ordre de tout cela.
    """
    g_carte = {}
    for cle, valeur in carte.items():
        famille = dict(FAMILLES).get(cle)
        if famille:
            g_carte[cle] = f"@produits:{famille}"
        elif cle == "menus":
            g_carte[cle] = "@menus"
        else:
            g_carte[cle] = valeur

    g_cfg = {cle: (f"@reglage:{COLONNES_REGLAGES[cle]}" if cle in COLONNES_REGLAGES
                   else valeur)
             for cle, valeur in cfg.items()}

    return {
        "carte": g_carte,
        "marches": {k: ("@marches" if k == "marches" else v)
                    for k, v in marches.items()},
        "avis": {k: ("@avis" if k == "avis" else v) for k, v in avis.items()},
        "config": g_cfg,
    }


# ==========================================================================
# Tables → JSON
# ==========================================================================

def _produit_json(p: dict) -> dict:
    """Un produit, avec les clés dans l'ordre et la forme du fichier d'origine.

    L'ordre suivi est celui de data/carte.json : nom, slug, prix, puis unite
    ou categorie selon la famille, puis vedette, puis description. Une clé
    absente du fichier d'origine ne doit pas apparaître — « vedette: false »
    sur une boisson serait une différence, donc un échec de la vérification.
    """
    o = {"nom": p["nom"], "slug": p["slug"], "prix": p["prix"]}
    if p["famille"] == "plat":
        o["categorie"] = p["categorie"]
    elif p["unite"] is not None:
        o["unite"] = p["unite"]
    if p["famille"] in ("plat", "entree"):
        o["vedette"] = p["vedette"]
    o["description"] = p["description"]
    return o


def _menu_json(m: dict, lignes: list[dict]) -> dict:
    o = {"nom": m["nom"], "slug": m["slug"], "prix": m["prix"],
         "prixMax": m["prix_max"]}
    if m["supplement_motif"] is not None:
        o["supplementMotif"] = m["supplement_motif"]
    o["resume"] = m["resume"]
    for bloc, cle in BLOCS_MENU:
        contenu = [l["libelle"] for l in sorted(lignes, key=lambda x: x["ordre"])
                   if l["menu_slug"] == m["slug"] and l["bloc"] == bloc]
        if contenu:
            o[cle] = contenu
    return o


def _ranger(lignes: list[dict]) -> list[dict]:
    """Les lignes actives, dans l'ordre voulu par le backoffice."""
    return sorted((l for l in lignes if l.get("actif", True)),
                  key=lambda l: l["ordre"])


def vers_json(tables: dict) -> dict:
    """Reconstitue les quatre documents JSON à partir des tables.

    C'est ici que le gabarit sert : on le parcourt, et chaque repère est
    remplacé par les données correspondantes. Tout ce qui n'est pas un repère
    est recopié tel quel, à sa place.
    """
    g = tables["reglages"]["gabarits"]

    listes = {f"@produits:{famille}":
              [_produit_json(p) for p in _ranger(tables["produits"])
               if p["famille"] == famille]
              for _, famille in FAMILLES}
    listes["@menus"] = [_menu_json(m, tables["menu_lignes"])
                        for m in _ranger(tables["menus"])]
    listes["@marches"] = [{
        "lieu": m["lieu"], "jour": m["jour"], "type": m["type"],
        "horaire": m["horaire"], "precision": m["details"],
        "jusquau": m["jusquau"] or "",
    } for m in _ranger(tables["marches"])]
    listes["@avis"] = [{
        "auteur": a["auteur"], "note": a["note"],
        "contexte": a["contexte"], "texte": a["texte"],
    } for a in sorted((a for a in tables["avis"] if a["publie"]),
                      key=lambda a: a["ordre"])]

    reglages = tables["reglages"]

    def remplir(gabarit: dict) -> dict:
        sortie = {}
        for cle, valeur in gabarit.items():
            if isinstance(valeur, str) and valeur in listes:
                sortie[cle] = listes[valeur]
            elif isinstance(valeur, str) and valeur.startswith("@reglage:"):
                sortie[cle] = reglages[valeur[len("@reglage:"):]]
            else:
                sortie[cle] = valeur
        return sortie

    return {nom: remplir(g[nom]) for nom in ("carte", "marches", "avis", "config")}


def ecrire_json(documents: dict) -> list[str]:
    """Écrit les quatre fichiers dans data/, au format exact des originaux.

    indent=2, ensure_ascii=False et une ligne vide finale : c'est ce que
    produit admin.html, et toute autre mise en forme ferait apparaître le
    fichier entier comme modifié à chaque publication.
    """
    ecrits = []
    for nom, contenu in documents.items():
        chemin = DATA / f"{nom}.json"
        chemin.write_text(json.dumps(contenu, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8", newline="\n")
        ecrits.append(chemin.name)
    return ecrits
