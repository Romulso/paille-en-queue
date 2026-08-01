#!/usr/bin/env python3
"""Génère la carte en PDF à partir de data/carte.json.

Le PDF est un document que les mairies et les comités d'entreprise font
circuler en interne : il doit donc porter les mêmes prix que le site, sans
risque de décalage. C'est pourquoi il est reconstruit depuis la même source.

À relancer après toute modification des plats, des menus ou des tarifs :

    cd /Users/admin/Projets/paille-en-queue
    PYTHONPATH=<dossier des paquets python> python3 outils/generer-menu-pdf.py

Dépendances : fpdf2. Les polices TTF de outils/polices/ sont converties depuis
fonts/*.woff2 (voir fontTools) et ne servent qu'ici.
"""

import json
import pathlib
import sys
from datetime import date

from fpdf import FPDF

RACINE = pathlib.Path(__file__).resolve().parent.parent
SORTIE = RACINE / "documents" / "carte-le-paille-en-queue.pdf"

PIMENT = (196, 41, 31)
PIMENT_SOMBRE = (141, 26, 18)
VETIVER = (16, 80, 63)
CURCUMA = (230, 161, 42)
ENCRE = (36, 26, 21)
ENCRE_DOUCE = (107, 86, 75)
VANILLE = (255, 249, 240)
SABLE = (244, 223, 198)


def euros(n):
    if n is None:
        return "sur devis"
    return f"{n} €" if float(n).is_integer() else f"{n:.2f} €".replace(".", ",")


class Carte(FPDF):
    def __init__(self, cfg):
        super().__init__(format="A4", unit="mm")
        self.cfg = cfg
        self.set_auto_page_break(True, margin=20)
        p = RACINE / "outils" / "polices"
        self.add_font("titre", "", p / "Fraunces.ttf")
        self.add_font("texte", "", p / "Outfit.ttf")

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("texte", size=8)
        self.set_text_color(*ENCRE_DOUCE)
        self.set_xy(20, 10)
        self.cell(0, 5, "Le Paille en Queue — spécialités créoles", align="L")
        # Le contenu reprend sous le bandeau, sinon il s'écrit par-dessus.
        self.set_xy(20, 22)

    def footer(self):
        self.set_y(-15)
        self.set_font("texte", size=8)
        self.set_text_color(*ENCRE_DOUCE)
        self.cell(0, 5, f"lepaille-en-queue.fr · {self.cfg['telephone']}", align="L")
        self.cell(0, 5, f"{self.page_no()}/{{nb}}", align="R")

    # ---------- briques de mise en page ----------

    def bandeau(self):
        """Bandeau de tête : logo sur fond piment, nom et coordonnées."""
        self.set_fill_color(*PIMENT)
        self.rect(0, 0, 210, 46, "F")
        logo = RACINE / "images" / "logo-blanc.png"
        if logo.exists():
            self.image(str(logo), x=20, y=8, h=30)
        self.set_xy(70, 12)
        self.set_font("titre", size=22)
        self.set_text_color(255, 255, 255)
        self.cell(0, 9, "Le Paille en Queue", align="L")
        self.set_xy(70, 22)
        self.set_font("texte", size=10)
        self.set_text_color(255, 235, 205)
        self.cell(0, 6, "Traiteur créole et réunionnais en Dordogne depuis 2009", align="L")
        self.set_xy(70, 29)
        self.cell(0, 6, f"{self.cfg['telephone']} · {self.cfg['email']}", align="L")
        self.set_y(56)

    def titre_section(self, texte, sous_titre=""):
        # Un titre ne doit jamais rester seul en bas de page : on garde de
        # quoi loger le titre et au moins un plat en dessous.
        if self.get_y() > 232:
            self.add_page()
        self.ln(3)
        self.set_font("titre", size=15)
        self.set_text_color(*PIMENT_SOMBRE)
        self.cell(0, 8, texte, new_x="LMARGIN", new_y="NEXT")
        if sous_titre:
            self.set_font("texte", size=9)
            self.set_text_color(*ENCRE_DOUCE)
            self.multi_cell(0, 4.6, sous_titre, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*CURCUMA)
        self.set_line_width(0.6)
        y = self.get_y() + 1.5
        self.line(20, y, 45, y)
        self.ln(4)

    def ligne_plat(self, nom, prix, unite, description=""):
        """Un plat : nom à gauche, prix à droite, description en dessous."""
        if self.get_y() > 258:
            self.add_page()
        self.set_font("texte", size=10.5)
        self.set_text_color(*ENCRE)
        largeur_prix = 32
        self.cell(170 - largeur_prix, 5.4, nom, align="L")
        self.set_font("titre", size=11)
        self.set_text_color(*PIMENT)
        self.cell(largeur_prix, 5.4, f"{prix}  {unite}".strip(), align="R",
                  new_x="LMARGIN", new_y="NEXT")
        if description:
            self.set_font("texte", size=8.4)
            self.set_text_color(*ENCRE_DOUCE)
            self.multi_cell(170, 3.9, description, new_x="LMARGIN", new_y="NEXT")
        self.ln(1.6)

    def encadre(self, titre, lignes, fond=SABLE):
        haut = 9 + 4.8 * len(lignes)
        if self.get_y() + haut > 268:
            self.add_page()
        y0 = self.get_y()
        self.set_fill_color(*fond)
        self.rect(20, y0, 170, haut, "F")
        self.set_xy(24, y0 + 2.5)
        self.set_font("titre", size=10.5)
        self.set_text_color(*VETIVER)
        self.cell(0, 5, titre, new_x="LMARGIN", new_y="NEXT")
        self.set_font("texte", size=9)
        self.set_text_color(*ENCRE)
        for l in lignes:
            self.set_x(24)
            self.cell(0, 4.6, l, new_x="LMARGIN", new_y="NEXT")
        self.set_y(y0 + haut + 5)


def construire():
    carte = json.loads((RACINE / "data" / "carte.json").read_text(encoding="utf-8"))
    cfg = json.loads((RACINE / "data" / "config.json").read_text(encoding="utf-8"))

    pdf = Carte(cfg)
    pdf.add_page()
    pdf.bandeau()
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)

    pdf.titre_section("Nos plats", carte["mentionPart"] + " " + carte["mentionMinimum"])
    for p in carte["plats"]:
        pdf.ligne_plat(p["nom"], euros(p["prix"]), "la part", p["description"])

    pdf.titre_section("Entrées et apéritif")
    for p in carte["entrees"]:
        pdf.ligne_plat(p["nom"], euros(p["prix"]), p.get("unite", ""), p["description"])

    pdf.titre_section("Pour trinquer")
    for p in carte["boissons"]:
        pdf.ligne_plat(p["nom"], euros(p["prix"]), p.get("unite", ""), p["description"])
    pdf.set_font("texte", size=7.6)
    pdf.set_text_color(*ENCRE_DOUCE)
    pdf.multi_cell(170, 3.6, "L'abus d'alcool est dangereux pour la santé. À consommer avec modération.",
                   new_x="LMARGIN", new_y="NEXT")

    pdf.titre_section("Nos trois menus", "Entrée, plat au choix et dessert. Prix par personne.")
    for m in carte["menus"]:
        prix = euros(m["prix"]) if not m.get("prixMax") else f"{m['prix']} à {m['prixMax']} €"
        pdf.set_font("titre", size=12.5)
        pdf.set_text_color(*VETIVER)
        pdf.cell(120, 7, m["nom"], align="L")
        pdf.set_text_color(*PIMENT)
        pdf.cell(50, 7, prix, align="R", new_x="LMARGIN", new_y="NEXT")
        if m.get("supplementMotif"):
            pdf.set_font("texte", size=8)
            pdf.set_text_color(*ENCRE_DOUCE)
            pdf.multi_cell(170, 4, f"Le prix haut s'applique {m['supplementMotif']}.",
                           new_x="LMARGIN", new_y="NEXT")
        for etiquette, cle in (("Entrée", "entree"), ("Plat au choix", "plats"),
                               ("Dessert", "dessert"), ("Compris", "inclus")):
            if not m.get(cle):
                continue
            pdf.set_font("texte", size=8.4)
            pdf.set_text_color(*CURCUMA)
            pdf.cell(26, 4.6, etiquette.upper(), align="L")
            pdf.set_text_color(*ENCRE)
            pdf.multi_cell(144, 4.6, " · ".join(m[cle]), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    pdf.titre_section("En supplément", carte["mentionNonCompris"])
    for s in carte["supplements"]:
        pdf.ligne_plat(s["nom"], euros(s["prix"]),
                       s["unite"] if s["prix"] is not None else "", s["description"])

    pdf.encadre("Conditions", [
        f"Commande à partir de {cfg['minimumParts']} parts, {cfg['delaiCommande']} à l'avance.",
        f"Déplacement jusqu'à {cfg['rayonLivraisonKm']} km autour de {cfg['villeAffichee']} : "
        f"{cfg['fraisLivraisonProche']} € jusqu'à 10 km, {cfg['fraisLivraisonLoin']} € au-delà. Plus loin, sur devis.",
        f"À partir de {cfg['seuilCuisineSurPlace']} convives, nous cuisinons sur le lieu de l'événement.",
        f"Devis valable {cfg['validiteDevis']}. {cfg['acompte']} % d'acompte à la signature, solde à la livraison.",
        "Règlement en espèces avec reçu, par chèque ou par virement.",
    ])

    serieux = [
        "Karine Danna est titulaire de la formation obligatoire à l'hygiène alimentaire (HACCP).",
        "L'entreprise est couverte par une assurance responsabilité civile professionnelle.",
    ]
    if cfg.get("controleOrganisme"):
        serieux.append(
            f"Contrôlés par l'{cfg['controleOrganisme']} de {cfg['controleVille']}, organisme indépendant : "
            f"résultat qualité {cfg['controleAnnee']} « {cfg['controleResultat']} ».")
    serieux.append(f"SIRET {cfg['siret']} · {cfg['rcs']} · Code APE {cfg['ape']}")
    pdf.encadre("Notre sérieux", serieux, fond=(226, 240, 232))

    pdf.set_font("texte", size=9)
    pdf.set_text_color(*ENCRE_DOUCE)
    pdf.multi_cell(170, 4.8,
                   f"Devis gratuit sous 48 h sur lepaille-en-queue.fr/devis.html\n"
                   f"{cfg['telephone']} · {cfg['email']}\n"
                   f"Tarifs au {date.today().strftime('%d/%m/%Y')}, susceptibles d'évoluer. "
                   f"Seul le devis nominatif fait foi.",
                   new_x="LMARGIN", new_y="NEXT")

    SORTIE.parent.mkdir(exist_ok=True)
    pdf.output(str(SORTIE))
    return SORTIE


if __name__ == "__main__":
    chemin = construire()
    print(f"  {chemin.relative_to(RACINE)}  {chemin.stat().st_size / 1024:.0f} Ko")
