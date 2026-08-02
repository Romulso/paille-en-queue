#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur du contenu statique des pages.

Pourquoi ce script existe
-------------------------
Le contenu du site vit dans data/*.json et site.js le met en page dans le
navigateur. C'est pratique à modifier depuis admin.html, mais un moteur de
recherche qui n'exécute pas JavaScript (Bing, GPTBot, PerplexityBot…) ne voit
alors qu'une page vide : ni les plats, ni les prix, ni les marchés.

Ce script écrit dans les .html la même chose que site.js écrirait, entre des
balises repères <!--auto:zone-xxx-->. site.js continue d'écraser ce contenu à
l'exécution : le visiteur voit toujours la version la plus fraîche, le robot
voit au moins la dernière version générée.

Usage
-----
    python outils/generer-html.py

À relancer après chaque modification du contenu depuis admin.html.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

# La console Windows est en cp1252 par défaut : sans cela, le moindre accent
# dans un message fait planter le script après avoir écrit les fichiers.
for flux in (sys.stdout, sys.stderr):
    if hasattr(flux, "reconfigure"):
        flux.reconfigure(encoding="utf-8", errors="replace")

RACINE = Path(__file__).resolve().parent.parent
DATA = RACINE / "data"

SITE = "https://lepaille-en-queue.fr"

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
JOURS_COURTS = {j: j[:3] for j in JOURS}
# schema.org attend les jours en anglais (DayOfWeek).
JOURS_SCHEMA = {
    "lundi": "Monday", "mardi": "Tuesday", "mercredi": "Wednesday",
    "jeudi": "Thursday", "vendredi": "Friday", "samedi": "Saturday",
    "dimanche": "Sunday",
}
# Les pages indexables. « service » n'est rempli que pour les pages piliers :
# ce sont les seules à décrire une prestation vendable.
PAGES = [
    {"fichier": "index.html", "nom": "Traiteur réunionnais en Dordogne — Le Paille en Queue"},
    {"fichier": "carte.html", "nom": "La carte et les menus créoles — Le Paille en Queue"},
    {"fichier": "marches.html", "nom": "Nos marchés nocturnes en Dordogne — Le Paille en Queue"},
    {"fichier": "zone-livraison.html",
     "nom": "Zone de livraison : traiteur créole en Dordogne et Gironde — Le Paille en Queue",
     "service": "Livraison de repas créoles",
     "service_desc": "Livraison de plats et menus créoles dans un rayon de 50 km "
                     "autour de Montpeyroux, sur l'ouest de la Dordogne et l'est "
                     "de la Gironde."},
    {"fichier": "devis.html", "nom": "Demander un devis traiteur — Le Paille en Queue"},
    {"fichier": "faq.html", "nom": "Questions fréquentes — Le Paille en Queue"},
    {"fichier": "evenements.html",
     "nom": "Traiteur événementiel en Dordogne — Le Paille en Queue",
     "service": "Traiteur événementiel",
     "service_desc": "Buffets et repas assis créoles pour séminaires, fêtes "
                     "communales, repas de club et grandes occasions en Dordogne."},
    {"fichier": "mariage.html",
     "nom": "Traiteur mariage en Dordogne — Le Paille en Queue",
     "service": "Traiteur mariage",
     "service_desc": "Vin d'honneur, repas assis ou buffet créole pour votre "
                     "mariage en Dordogne, cuisiné sur place dès 50 convives."},
    {"fichier": "entreprise.html",
     "nom": "Traiteur entreprise en Dordogne — Le Paille en Queue",
     "service": "Traiteur d'entreprise",
     "service_desc": "Séminaires, inaugurations, pots de départ et repas du "
                     "personnel. Devis, facture, HACCP et assurance professionnelle."},
    {"fichier": "collectivites.html",
     "nom": "Traiteur pour communes et associations — Le Paille en Queue",
     "service": "Traiteur pour collectivités et associations",
     "service_desc": "Fêtes communales, repas des aînés, clubs sportifs et "
                     "associations. Grands volumes et cuisson sur place."},
]

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
MOIS_COURTS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.",
               "août", "sept.", "oct.", "nov.", "déc."]


# --------------------------------------------------------------------------
# Utilitaires — mêmes règles que site.js, pour que le HTML généré et le HTML
# injecté par le navigateur soient identiques au caractère près.
# --------------------------------------------------------------------------

def echapper(s) -> str:
    """Équivalent de la fonction echapper() de site.js."""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def euros(n) -> str:
    """10 → « 10 € », 0.4 → « 0,40 € », None → « sur devis »."""
    if n is None:
        return "sur devis"
    if isinstance(n, float) and not n.is_integer():
        return f"{n:.2f}".replace(".", ",") + " €"
    return f"{int(n)} €"


def lire(nom: str) -> dict:
    chemin = DATA / f"{nom}.json"
    with chemin.open(encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------------------
# Gabarits — transcription des fonctions du même nom dans site.js
# --------------------------------------------------------------------------

def sources_photo(slug: str) -> str:
    """Les <source> AVIF et WebP, uniquement si les fichiers existent.

    Dans un <picture>, le navigateur s'engage sur la première source dont le
    type lui convient : si le .avif est annoncé mais absent, il ne se rabat pas
    sur le .jpg, il n'affiche rien. On n'annonce donc que ce qui existe
    vraiment sur le disque au moment de la génération.
    """
    lignes = []
    for extension, mime in (("avif", "image/avif"), ("webp", "image/webp")):
        if (RACINE / "images" / f"{slug}.{extension}").exists():
            lignes.append(f'            <source type="{mime}" '
                          f'srcset="images/{echapper(slug)}.{extension}">')
    return ("\n" + "\n".join(lignes)) if lignes else ""


def gabarit_plat(p: dict, unite: str = "la part") -> str:
    vedette = ('<span class="etiquette-vedette">Signature</span>'
               if p.get("vedette") else "")
    return f"""
      <article class="plat apparait" data-categorie="{echapper(p.get('categorie', ''))}">
        <div class="photo" data-nom="{echapper(p['nom'])}">
          {vedette}
          <picture>{sources_photo(p['slug'])}
            <img src="images/{echapper(p['slug'])}.jpg" alt="{echapper(p['nom'])}, plat créole préparé par Le Paille en Queue, traiteur réunionnais en Dordogne" loading="lazy" decoding="async" width="600" height="450">
          </picture>
        </div>
        <div class="plat-corps">
          <div class="plat-tete">
            <h3>{echapper(p['nom'])}</h3>
            <span class="prix">{euros(p.get('prix'))}<small>{echapper(p.get('unite') or unite)}</small></span>
          </div>
          <p>{echapper(p['description'])}</p>
        </div>
      </article>"""


def gabarit_formule(m: dict, vedette: bool) -> str:
    def bloc(titre: str, lignes) -> str:
        if not lignes:
            return ""
        items = "".join(f"<li>{echapper(l)}</li>" for l in lignes)
        return f"""
      <div class="formule-bloc">
        <h4>{titre}</h4>
        <ul>{items}</ul>
      </div>"""

    prix_max = m.get("prixMax")
    prix = (f"{m['prix']} <span>à</span> {prix_max} <span>€</span>"
            if prix_max else f"{m['prix']} <span>€</span>")
    detail = (f"par personne — {prix_max} € "
              f"{echapper(m.get('supplementMotif') or 'selon le plat choisi')}"
              if prix_max else "par personne")
    ruban = '<span class="formule-ruban">Le plus demandé</span>' if vedette else ""
    inclus = m.get("inclus") or []
    ligne_inclus = (f'<p class="formule-inclus">Compris : '
                    f'{" · ".join(echapper(i) for i in inclus)}.</p>' if inclus else "")

    return f"""
      <article class="formule apparait{' formule-vedette' if vedette else ''}">
        {ruban}
        <h3>{echapper(m['nom'])}</h3>
        <p class="formule-prix">{prix}<small>{detail}</small></p>
        <p>{echapper(m['resume'])}</p>
        {bloc("Entrée", m.get("entree"))}
        {bloc("Plat au choix", m.get("plats"))}
        {bloc("Dessert", m.get("dessert"))}
        {ligne_inclus}
        <a class="pastille pastille-pleine" href="devis.html?menu={echapper(m['slug'])}">Demander ce menu</a>
      </article>"""


def gabarit_supplement(s: dict) -> str:
    unite = "" if s.get("prix") is None else f"<small>{echapper(s.get('unite', ''))}</small>"
    return f"""
        <article class="supplement apparait">
          <h3>{echapper(s['nom'])}</h3>
          <span class="prix">{euros(s.get('prix'))}{unite}</span>
          <p>{echapper(s['description'])}</p>
        </article>"""


def gabarit_marche(m: dict) -> str:
    est_date = bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(m.get("jour", ""))))
    if est_date:
        d = datetime.strptime(m["jour"], "%Y-%m-%d")
        haut, bas = str(d.day), MOIS_COURTS[d.month - 1]
    else:
        haut, bas = str(m["jour"])[:3], "chaque semaine"

    lignes = ""
    if m.get("horaire"):
        lignes += f"\n            <p>{echapper(m['horaire'])}</p>"
    if m.get("precision"):
        lignes += f"\n            <p>{echapper(m['precision'])}</p>"
    if m.get("jusquau"):
        fin = datetime.strptime(m["jusquau"], "%Y-%m-%d")
        lignes += (f"\n            <p>Jusqu'au {fin.day} "
                   f"{MOIS[fin.month - 1]}</p>")

    nocturne = m.get("type") == "nocturne"
    return f"""
        <article class="marche apparait">
          <div class="marche-jour"><b>{echapper(haut)}</b>{echapper(bas)}</div>
          <div>
            <h3>{echapper(m['lieu'])}</h3>{lignes}
            <span class="marche-type {'nocturne' if nocturne else ''}">
              {'Marché nocturne' if nocturne else 'Marché du matin'}
            </span>
          </div>
        </article>"""


def gabarit_zone(zone: dict, cfg: dict) -> str:
    """Les communes desservies, groupées par tranche de distance.

    Groupées plutôt qu'en liste plate : le visiteur cherche « est-ce qu'ils
    viennent chez moi », et la tranche lui donne du même coup le prix de la
    livraison.
    """
    tranches = [
        (0, 10, f"À moins de 10 km — livraison {cfg['fraisLivraisonProche']} €"),
        (11, 20, f"De 10 à 20 km — livraison {cfg['fraisLivraisonLoin']} €"),
        (21, 35, f"De 20 à 35 km — livraison {cfg['fraisLivraisonLoin']} €"),
        (36, 50, f"De 35 à 50 km — livraison {cfg['fraisLivraisonLoin']} €"),
    ]
    blocs = []
    for mini, maxi, titre in tranches:
        dedans = [c for c in zone["communes"] if mini <= c["km"] <= maxi]
        if not dedans:
            continue
        items = "".join(
            f'\n            <li><b>{echapper(c["nom"])}</b> '
            f'<span>{echapper(c["cp"])} · {c["km"]} km</span></li>'
            for c in dedans)
        blocs.append(f"""
        <div class="zone-tranche apparait">
          <h3>{echapper(titre)}</h3>
          <ul class="zone-communes">{items}
          </ul>
        </div>""")
    return "".join(blocs)


def gabarit_avis(a: dict) -> str:
    initiale = (a.get("auteur") or "?").strip()[:1].upper()
    note = a.get("note")
    etoiles = (f'<div class="etoiles" aria-label="{note} sur 5">'
               f'{"★" * note}{"☆" * (5 - note)}</div>' if note else "")
    contexte = f"<small>{echapper(a['contexte'])}</small>" if a.get("contexte") else ""
    return f"""
      <article class="avis apparait">
        {etoiles}
        <p>« {echapper(a['texte'])} »</p>
        <footer>
          <span class="avatar" aria-hidden="true">{echapper(initiale)}</span>
          <span>
            <b>{echapper(a['auteur'])}</b>
            {contexte}
          </span>
        </footer>
      </article>"""


def avis_vide(cfg: dict) -> str:
    """L'invitation affichée tant qu'aucun témoignage n'a été saisi.

    On envoie vers Google plutôt que vers la boîte mail : un avis Google est
    visible par le client suivant, et il compte pour le référencement local.
    Un avis reçu par e-mail ne fait ni l'un ni l'autre.
    """
    fiche = cfg.get("googleBusinessProfile")
    bouton = (f'<a class="pastille pastille-pleine" rel="noopener"\n'
              f'               href="{echapper(fiche)}">Laisser un avis sur Google</a>'
              if fiche else
              '<a class="pastille pastille-pleine"\n'
              '               href="mailto:contact@lepaille-en-queue.fr?subject=Mon%20avis%20sur%20Le%20Paille%20en%20Queue"\n'
              '               data-cfg-href="email|mailto:">Laisser un avis</a>')
    return f"""
        <div class="etat-vide">
          <h3>Les premiers avis arrivent</h3>
          <p>
            Vous avez fait appel à nous pour un repas ou un événement&nbsp;?
            Votre retour aide énormément les personnes qui hésitent encore.
          </p>
          <p style="margin-top:18px">
            {bouton}
          </p>
        </div>"""

MARCHES_VIDE = """
        <div class="etat-vide">
          <h3>Le calendrier arrive</h3>
          <p>Nos dates de marchés pour la saison sont en cours de mise à jour.
             Appelez Karine au <a href="tel:+33627352328"><b>06 27 35 23 28</b></a>
             pour savoir où nous retrouver cette semaine.</p>
        </div>"""


# --------------------------------------------------------------------------
# Données structurées — écrites en dur plutôt qu'injectées par site.js, pour
# les mêmes raisons que le contenu : un robot sans JavaScript doit les voir.
# --------------------------------------------------------------------------

def schema_entreprise(cfg: dict) -> dict:
    """La fiche d'identité de l'entreprise, construite depuis data/config.json.

    Elle est répétée sur chaque page plutôt que définie une seule fois sur
    l'accueil : le poids est négligeable (~1,5 Ko) et cela évite de dépendre de
    la capacité de Google à relier des @id entre deux pages.
    """
    rue, _, reste = cfg["adresseLegale"].partition(",")
    code_postal, _, ville = reste.strip().partition(" ")

    sameas = [u for u in (cfg.get("facebook"), cfg.get("instagram"),
                          cfg.get("googleBusinessProfile")) if u]

    entreprise = {
        "@type": "FoodEstablishment",
        "@id": f"{SITE}/#entreprise",
        "name": cfg["entreprise"],
        "alternateName": f"{cfg['entreprise']} — {cfg['baseline']}",
        "description": (
            "Traiteur ambulant spécialisé en cuisine réunionnaise et créole, en "
            f"{cfg['departement']} depuis {cfg['creation']}. Repas livrés à partir "
            f"de {cfg['minimumParts']} parts, buffets et prestations événementielles."),
        "url": f"{SITE}/",
        "logo": f"{SITE}/images/logo@2x.png",
        "image": f"{SITE}/images/partage.jpg",
        "telephone": cfg["telephoneLien"],
        "email": cfg["email"],
        "foundingDate": str(cfg["creation"]),
        "servesCuisine": ["Réunionnaise", "Créole"],
        "priceRange": "10 € - 30 €",
        "currenciesAccepted": "EUR",
        "paymentAccepted": "Espèces, Chèque, Virement bancaire",
        "hasMenu": f"{SITE}/carte.html",
        "identifier": {"@type": "PropertyValue", "propertyID": "SIRET",
                       "value": cfg["siret"]},
        "founder": {"@type": "Person", "name": cfg["gerante"]},
        "address": {
            "@type": "PostalAddress",
            "streetAddress": rue.strip(),
            "postalCode": code_postal,
            "addressLocality": ville,
            "addressRegion": cfg["departement"],
            "addressCountry": "FR",
        },
        "areaServed": [
            {"@type": "AdministrativeArea", "name": "Dordogne"},
            {"@type": "AdministrativeArea", "name": "Gironde"},
            {"@type": "City", "name": "Montpeyroux"},
            {"@type": "City", "name": "Montpon-Ménestérol"},
            {"@type": "City", "name": "Le Pizou"},
            {"@type": "City", "name": "Saint-Laurent-des-Hommes"},
            {"@type": "City", "name": "Saint-Seurin-sur-l'Isle"},
        ],
        "makesOffer": [
            {
                "@type": "Offer",
                "name": "Repas créole livré",
                "description": ("Plats réunionnais livrés prêts à servir, à partir "
                                f"de {cfg['minimumParts']} parts. Riz et sauce "
                                "piquante compris."),
                "priceSpecification": {
                    "@type": "PriceSpecification", "minPrice": 10, "maxPrice": 12,
                    "priceCurrency": "EUR", "valueAddedTaxIncluded": True,
                },
            },
            {
                "@type": "Offer",
                "name": "Menu complet pour événement",
                "description": ("Entrée, plat au choix et dessert, pour mariages, "
                                "repas d'entreprise, fêtes communales et repas "
                                "d'association."),
                "priceSpecification": {
                    "@type": "PriceSpecification", "minPrice": 18, "maxPrice": 30,
                    "priceCurrency": "EUR", "valueAddedTaxIncluded": True,
                },
            },
        ],
    }

    if sameas:
        entreprise["sameAs"] = sameas
    if cfg.get("googleBusinessProfile"):
        entreprise["hasMap"] = cfg["googleBusinessProfile"]
    # Des coordonnées fausses feraient apparaître l'entreprise au mauvais
    # endroit sur Google Maps : mieux vaut rien que n'importe quoi.
    if cfg.get("latitude") and cfg.get("longitude"):
        entreprise["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": float(cfg["latitude"]),
            "longitude": float(cfg["longitude"]),
        }
        entreprise["serviceArea"] = {
            "@type": "GeoCircle",
            "geoMidpoint": {"@type": "GeoCoordinates",
                            "latitude": float(cfg["latitude"]),
                            "longitude": float(cfg["longitude"])},
            "geoRadius": cfg["rayonLivraisonKm"] * 1000,
        }
    return entreprise


def schema_service(page: dict, cfg: dict) -> dict:
    return {
        "@type": "Service",
        "@id": f"{SITE}/{page['fichier']}#service",
        "name": page["service"],
        "serviceType": page["service"],
        "description": page["service_desc"],
        "provider": {"@id": f"{SITE}/#entreprise"},
        "areaServed": [{"@type": "AdministrativeArea", "name": "Dordogne"},
                       {"@type": "AdministrativeArea", "name": "Gironde"}],
        "offers": {
            "@type": "Offer",
            "priceSpecification": {
                "@type": "PriceSpecification", "minPrice": 18, "maxPrice": 30,
                "priceCurrency": "EUR", "valueAddedTaxIncluded": True,
                "description": "Par personne, menu complet",
            },
            "availability": "https://schema.org/InStock",
        },
    }


def schema_page(page: dict, cfg: dict) -> dict:
    """Le bloc commun à toutes les pages : le site, la page, l'entreprise."""
    url = f"{SITE}/" if page["fichier"] == "index.html" else f"{SITE}/{page['fichier']}"
    graphe = [
        schema_entreprise(cfg),
        {
            "@type": "WebSite",
            "@id": f"{SITE}/#site",
            "url": f"{SITE}/",
            "name": cfg["entreprise"],
            "inLanguage": "fr-FR",
            "publisher": {"@id": f"{SITE}/#entreprise"},
        },
        {
            "@type": "WebPage",
            "@id": f"{url}#page",
            "url": url,
            "name": page["nom"],
            "inLanguage": "fr-FR",
            "isPartOf": {"@id": f"{SITE}/#site"},
            "about": {"@id": f"{SITE}/#entreprise"},
            "primaryImageOfPage": {"@type": "ImageObject",
                                   "url": f"{SITE}/images/partage.jpg"},
        },
    ]
    if page.get("service"):
        graphe.append(schema_service(page, cfg))
    return {"@context": "https://schema.org", "@graph": graphe}


def schema_menu(d: dict) -> dict:
    def article(p):
        return {
            "@type": "MenuItem",
            "name": p["nom"],
            "description": p["description"],
            "offers": {
                "@type": "Offer",
                "price": p.get("prix"),
                "priceCurrency": "EUR",
                "description": p.get("unite") or "la part",
            },
        }

    def section(nom, liste):
        return {"@type": "MenuSection", "name": nom,
                "hasMenuItem": [article(p) for p in liste]}

    return {
        "@context": "https://schema.org",
        "@type": "Menu",
        "name": "La carte du Paille en Queue",
        "inLanguage": "fr-FR",
        "url": f"{SITE}/carte.html",
        "provider": {"@id": f"{SITE}/#entreprise"},
        "hasMenuSection": [
            section("Plats créoles", d["plats"]),
            section("Entrées et apéritif", d["entrees"]),
            section("Boissons", d["boissons"]),
            {
                "@type": "MenuSection",
                "name": "Menus complets",
                "hasMenuItem": [{
                    "@type": "MenuItem",
                    "name": m["nom"],
                    "description": m["resume"],
                    "offers": {
                        "@type": "Offer",
                        "price": m["prix"],
                        "priceCurrency": "EUR",
                        "description": (
                            f"Par personne, jusqu'à {m['prixMax']} € "
                            f"{m.get('supplementMotif', '')}".strip()
                            if m.get("prixMax") else "Par personne"),
                    },
                } for m in d["menus"]],
            },
        ],
    }


def schema_marches(liste: list) -> dict | None:
    """Les marchés hebdomadaires en Event + Schedule.

    Les marchés « communes variables » sont volontairement écartés : sans lieu
    précis, l'événement serait invalide et Google le rejetterait.
    """
    evenements = []
    for m in liste:
        lieu = m.get("lieu", "")
        if not lieu or "variable" in lieu.lower():
            continue
        jour = str(m.get("jour", ""))
        if jour not in JOURS_SCHEMA:
            continue  # date unique : géré au cas par cas, rare ici

        nocturne = m.get("type") == "nocturne"
        horaires = {"startTime": "19:00", "endTime": "23:00"} if nocturne else \
                   {"startTime": "08:00", "endTime": "13:00"}
        schedule = {
            "@type": "Schedule",
            "repeatFrequency": "P1W",
            "byDay": f"https://schema.org/{JOURS_SCHEMA[jour]}",
            "scheduleTimezone": "Europe/Paris",
            **horaires,
        }
        if m.get("jusquau"):
            schedule["endDate"] = m["jusquau"]

        evenements.append({
            "@type": "Event",
            "name": f"Le Paille en Queue au marché {'nocturne' if nocturne else 'du matin'} de {lieu}",
            "description": (m.get("precision") or
                            "Stand de plats créoles et réunionnais à emporter : "
                            "samoussas, bouchons, accras et plat du jour."),
            "eventSchedule": schedule,
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled",
            "location": {
                "@type": "Place",
                "name": f"Marché de {lieu}",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": lieu,
                    "addressRegion": "Nouvelle-Aquitaine",
                    "addressCountry": "FR",
                },
            },
            "organizer": {"@id": f"{SITE}/#entreprise"},
            "isAccessibleForFree": True,
            "image": f"{SITE}/images/stand.jpg",
        })

    if not evenements:
        return None
    return {"@context": "https://schema.org", "@graph": evenements}


# --------------------------------------------------------------------------
# Injection
# --------------------------------------------------------------------------

def injecter(html: str, zone: str, contenu: str) -> str:
    """Remplace le contenu entre les repères, ou les pose au premier passage."""
    debut, fin = f"<!--auto:{zone}-->", f"<!--/auto:{zone}-->"
    bloc = f"{debut}{contenu}\n      {fin}"

    motif_repere = re.compile(re.escape(debut) + r".*?" + re.escape(fin), re.S)
    if motif_repere.search(html):
        return motif_repere.sub(lambda _: bloc, html, count=1)

    # Premier passage : la zone est encore une balise vide.
    motif_vide = re.compile(
        r'(<(div|ul)[^>]*id="' + re.escape(zone) + r'"[^>]*>)\s*(</\2>)')
    if not motif_vide.search(html):
        raise SystemExit(f"  ! zone introuvable ou déjà remplie : {zone}")
    return motif_vide.sub(lambda m: f"{m.group(1)}{bloc}\n      {m.group(3)}",
                          html, count=1)


def injecter_schema(html: str, cle: str, donnees: dict | None) -> str:
    """Pose (ou remplace) un bloc JSON-LD identifié, juste avant </head>."""
    debut, fin = f"<!--auto:schema-{cle}-->", f"<!--/auto:schema-{cle}-->"
    if donnees is None:
        bloc = ""
    else:
        json_ld = json.dumps(donnees, ensure_ascii=False, indent=2)
        bloc = (f'{debut}\n<script type="application/ld+json" id="schema-{cle}">\n'
                f'{json_ld}\n</script>\n{fin}')

    motif = re.compile(re.escape(debut) + r".*?" + re.escape(fin), re.S)
    if motif.search(html):
        return motif.sub(lambda _: bloc, html, count=1)
    if not bloc:
        return html
    return html.replace("</head>", f"{bloc}\n</head>", 1)


def ecrire_sitemap() -> None:
    """Le plan du site, daté d'après la dernière modification réelle des pages.

    Des dates toutes identiques et jamais mises à jour finissent par être
    ignorées par Google : autant qu'elles disent la vérité.
    """
    priorites = {"index.html": "1.0", "carte.html": "0.9", "evenements.html": "0.9",
                 "devis.html": "0.8", "mariage.html": "0.8", "entreprise.html": "0.8",
                 "collectivites.html": "0.8", "zone-livraison.html": "0.8",
                 "marches.html": "0.7", "faq.html": "0.6"}
    frequences = {"marches.html": "weekly"}

    lignes = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for page in sorted(PAGES, key=lambda p: -float(priorites[p["fichier"]])):
        fichier = page["fichier"]
        chemin = RACINE / fichier
        modifie = date.fromtimestamp(chemin.stat().st_mtime).isoformat()
        url = f"{SITE}/" if fichier == "index.html" else f"{SITE}/{fichier}"
        lignes += [
            "  <url>",
            f"    <loc>{url}</loc>",
            f"    <lastmod>{modifie}</lastmod>",
            f"    <changefreq>{frequences.get(fichier, 'monthly')}</changefreq>",
            f"    <priority>{priorites[fichier]}</priority>",
            "  </url>",
        ]
    lignes.append("</urlset>")
    (RACINE / "sitemap.xml").write_text("\n".join(lignes) + "\n",
                                        encoding="utf-8", newline="\n")
    print("  ✓ sitemap.xml")


def ecrire(nom: str, html: str) -> None:
    chemin = RACINE / nom
    ancien = chemin.read_text(encoding="utf-8")
    if ancien == html:
        print(f"  = {nom} (inchangé)")
        return
    chemin.write_text(html, encoding="utf-8", newline="\n")
    print(f"  ✓ {nom}")


# --------------------------------------------------------------------------

def main() -> int:
    carte = lire("carte")
    marches_data = lire("marches")
    avis_data = lire("avis")
    cfg = lire("config")

    print("Génération du contenu statique…")

    # ---- données structurées communes à toutes les pages -----------------
    # Fait en premier : les injections de contenu qui suivent relisent les
    # fichiers depuis le disque.
    for page in PAGES:
        chemin = RACINE / page["fichier"]
        html = chemin.read_text(encoding="utf-8")
        html = injecter_schema(html, "entreprise", schema_page(page, cfg))
        ecrire(page["fichier"], html)

    if not (cfg.get("latitude") and cfg.get("longitude")):
        print("  ! coordonnées GPS absentes de data/config.json "
              "(admin.html → Réglages) : le champ geo est omis.")
    if not cfg.get("googleBusinessProfile"):
        print("  ! fiche Google absente de data/config.json "
              "(admin.html → Réglages) : hasMap est omis.")

    # ---- carte.html ------------------------------------------------------
    html = (RACINE / "carte.html").read_text(encoding="utf-8")
    html = injecter(html, "zone-plats",
                    "".join(gabarit_plat(p) for p in carte["plats"]))
    html = injecter(html, "zone-entrees",
                    "".join(gabarit_plat(p) for p in carte["entrees"]))
    html = injecter(html, "zone-boissons",
                    "".join(gabarit_plat(p) for p in carte["boissons"]))
    html = injecter(html, "zone-buffet",
                    "".join(f"\n        <li>{echapper(e)}</li>"
                            for e in carte["buffet"]["elements"]))
    html = injecter(html, "zone-supplements",
                    "".join(gabarit_supplement(s) for s in carte["supplements"]))
    html = injecter(html, "zone-menus",
                    "".join(gabarit_formule(m, i == 1)
                            for i, m in enumerate(carte["menus"])))
    html = injecter_schema(html, "carte", schema_menu(carte))
    ecrire("carte.html", html)

    # ---- index.html ------------------------------------------------------
    vedettes = [p for p in [*carte["plats"], *carte["entrees"]]
                if p.get("vedette")][:6]
    html = (RACINE / "index.html").read_text(encoding="utf-8")
    html = injecter(html, "zone-vedettes",
                    "".join(gabarit_plat(p) for p in vedettes))
    liste_avis = avis_data.get("avis") or []
    html = injecter(html, "zone-avis",
                    "".join(gabarit_avis(a) for a in liste_avis)
                    if liste_avis else avis_vide(cfg))
    ecrire("index.html", html)

    # ---- zone-livraison.html ---------------------------------------------
    zone = lire("zone")
    html = (RACINE / "zone-livraison.html").read_text(encoding="utf-8")
    html = injecter(html, "zone-communes", gabarit_zone(zone, cfg))
    ecrire("zone-livraison.html", html)

    # ---- marches.html ----------------------------------------------------
    aujourdhui = date.today().isoformat()
    tous = marches_data.get("marches") or []
    actifs = sorted(
        (m for m in tous if not m.get("jusquau") or m["jusquau"] >= aujourdhui),
        key=lambda m: (JOURS.index(m["jour"]) if m["jour"] in JOURS
                       else 100 + int(str(m["jour"]).replace("-", ""))))

    html = (RACINE / "marches.html").read_text(encoding="utf-8")
    html = injecter(html, "zone-marches",
                    "".join(gabarit_marche(m) for m in actifs)
                    if actifs else MARCHES_VIDE)
    # site.js pose cette classe à l'exécution ; sans JavaScript il faut qu'elle
    # soit déjà là, sinon la grille s'affiche en colonne.
    if actifs:
        html = html.replace('<div id="zone-marches">',
                            '<div class="grille-marches" id="zone-marches">', 1)
    html = injecter_schema(html, "marches", schema_marches(actifs))
    ecrire("marches.html", html)

    if not actifs:
        print("  ! aucun marché actif : marches.html affiche l'état vide.")

    # En dernier : les dates viennent de la modification des fichiers, qui
    # vient d'avoir lieu.
    ecrire_sitemap()
    print("Terminé.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
