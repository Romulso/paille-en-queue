#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fabrique les versions AVIF et WebP des photos.

Pourquoi
--------
Les photos sont ce qui pèse le plus lourd sur un site vitrine, et la vitesse
d'affichage est un critère de classement de Google — surtout sur téléphone, qui
représente l'essentiel des visites d'un traiteur.

Les mêmes images en AVIF pèsent trois à quatre fois moins qu'en JPEG, à qualité
équivalente. Les navigateurs choisissent tout seuls le format qu'ils savent
lire, et le JPEG d'origine reste le filet de sécurité : rien ne casse nulle
part.

Usage
-----
    python outils/optimiser-images.py          # ne refait que ce qui a changé
    python outils/optimiser-images.py --tout   # tout refaire

Les fichiers .avif et .webp produits doivent être commités avec les .jpg :
ils font partie du site publié.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow n'est pas installé. Lancez :\n"
             "    python3 -m pip install --user Pillow")

for flux in (sys.stdout, sys.stderr):
    if hasattr(flux, "reconfigure"):
        flux.reconfigure(encoding="utf-8", errors="replace")

IMAGES = Path(__file__).resolve().parent.parent / "images"

# Ces fichiers sont servis tels quels par le navigateur ou les réseaux sociaux,
# qui ne savent pas négocier de format : on n'y touche pas.
IGNORER = {"favicon.png", "partage.jpg"}

# Qualités choisies à l'œil sur les photos de plats : en dessous, le grain de
# la sauce et les reflets du riz commencent à se voir.
QUALITE_AVIF = 58
QUALITE_WEBP = 80

# Largeurs supplémentaires pour les grandes images d'ambiance. Une bannière de
# 2000 px envoyée à un téléphone de 390 px de large, c'est 90 % du poids jeté.
LARGEURS = {
    "accueil.jpg": [2000, 1400, 900],
    "panorama-reunion.jpg": [1800, 1100],
}


def derivees(source: Path, largeur: int | None) -> list[tuple[Path, str, dict]]:
    """Les fichiers à produire pour une source et une largeur données."""
    suffixe = "" if largeur is None else f"-{largeur}"
    base = source.with_suffix("")
    return [
        (Path(f"{base}{suffixe}.avif"), "AVIF", {"quality": QUALITE_AVIF}),
        (Path(f"{base}{suffixe}.webp"), "WEBP", {"quality": QUALITE_WEBP, "method": 6}),
    ]


def main() -> int:
    tout = "--tout" in sys.argv
    sources = sorted(p for p in IMAGES.iterdir()
                     if p.suffix.lower() in (".jpg", ".jpeg", ".png")
                     and p.name not in IGNORER)

    total_avant = total_apres = 0
    produits = ignores = 0

    for source in sources:
        largeurs = LARGEURS.get(source.name, [None])
        with Image.open(source) as image:
            image.load()
            origine = image
            for largeur in largeurs:
                if largeur is None or largeur >= origine.width:
                    variante = origine
                    cible_largeur = None if largeur is None else largeur
                    if cible_largeur is not None and largeur > origine.width:
                        continue
                else:
                    ratio = largeur / origine.width
                    variante = origine.resize(
                        (largeur, round(origine.height * ratio)),
                        Image.Resampling.LANCZOS)
                    cible_largeur = largeur

                for chemin, format_, options in derivees(source, cible_largeur):
                    frais = (chemin.exists()
                             and chemin.stat().st_mtime >= source.stat().st_mtime)
                    if frais and not tout:
                        ignores += 1
                        total_apres += chemin.stat().st_size
                        continue
                    a_ecrire = variante
                    # L'AVIF gère la transparence, mais Pillow veut du RGBA
                    # explicite pour les PNG à fond transparent.
                    if format_ == "AVIF" and a_ecrire.mode not in ("RGB", "RGBA"):
                        a_ecrire = a_ecrire.convert("RGBA")
                    a_ecrire.save(chemin, format_, **options)
                    produits += 1
                    total_apres += chemin.stat().st_size

        total_avant += source.stat().st_size

    print(f"{produits} fichier(s) produit(s), {ignores} déjà à jour.")
    if produits:
        print(f"Sources JPEG/PNG : {total_avant / 1024:.0f} Ko")
        print(f"Dérivés AVIF+WebP : {total_apres / 1024:.0f} Ko "
              f"(toutes tailles confondues)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
