#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Installe une photo depuis le disque dans le site.

Karine dépose ses photos depuis le backoffice ; ce script fait la même chose
depuis un fichier local, ce qui est plus pratique quand on en a plusieurs à
poser d'un coup.

Il applique exactement le même traitement que la publication : orientation
EXIF respectée, recadrage centré en 4:3, 1200 × 900, puis fabrication des
formats AVIF et WebP.

Usage
-----
    python outils/installer-photo.py <fichier> <slug>

Exemple
-------
    python outils/installer-photo.py ~/Downloads/rougail.jpg rougail-saucisses

Le slug doit correspondre à un plat de data/carte.json : c'est ce qui relie
la photo au plat. La liste s'affiche en cas d'erreur.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import modele  # noqa: E402
from importlib.machinery import SourceFileLoader  # noqa: E402

for flux in (sys.stdout, sys.stderr):
    if hasattr(flux, "reconfigure"):
        flux.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    if len(sys.argv) != 3:
        sys.exit("Usage : python outils/installer-photo.py <fichier> <slug>")

    source, slug = Path(sys.argv[1]).expanduser(), sys.argv[2]
    if not source.exists():
        sys.exit(f"Fichier introuvable : {source}")

    carte = modele.lire("carte")
    slugs = {p["slug"] for cle, _ in modele.FAMILLES for p in carte[cle]}
    if slug not in slugs:
        sys.exit(f"« {slug} » ne correspond à aucun plat.\n"
                 "Slugs disponibles :\n  " + "\n  ".join(sorted(slugs)))

    # On réutilise le traitement de la publication, pour que la photo posée
    # à la main soit identique à celle déposée depuis le backoffice.
    recup = SourceFileLoader("recup", str(Path(__file__).parent / "recuperer-photos.py")).load_module()
    image = recup.au_format(source.read_bytes())

    cible = modele.RACINE / "images" / f"{slug}.jpg"
    image.save(cible, quality=88, optimize=True, progressive=True)
    print(f"  ✓ images/{slug}.jpg  {image.size[0]}×{image.size[1]}  "
          f"{cible.stat().st_size / 1024:.0f} Ko")
    print("  Pensez à lancer outils/optimiser-images.py pour l'AVIF et le WebP.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
