#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Récupère les photos déposées depuis le backoffice et les range dans images/.

Place dans la chaîne
--------------------
Karine peut créer un plat depuis le backoffice, mais pas déposer sa photo dans
le dépôt : elle n'y a pas accès. Le backoffice envoie donc la photo dans un
bucket Supabase qui ne sert que de boîte de transit, et ce script la rapatrie
au moment de la publication.

Le site continue de servir ses propres fichiers : il ne dépend jamais de
Supabase pour afficher une image. C'est la contrainte du § 2 du cahier des
charges, et elle vaut aussi pour les photos.

Ce que le script fait
---------------------
1. liste le bucket ;
2. ne garde que les fichiers dont le nom correspond au slug d'un produit —
   un nom inconnu est ignoré, pour qu'un fichier égaré ne se retrouve pas
   dans le dépôt public ;
3. met la photo au format des autres : recadrage centré en 4:3, 1200 × 900 ;
4. l'écrit dans images/<slug>.jpg ;
5. vide le bucket : la photo est désormais dans git, la garder en double
   n'apporte rien et finirait par tout mélanger.

Usage
-----
    export SUPABASE_URL=https://xxxx.supabase.co
    export SUPABASE_SERVICE_KEY=sb_secret_...
    python outils/recuperer-photos.py

Sans photo à traiter, le script ne fait rien et sort en 0.
Dépendance : Pillow (le reste est dans la bibliothèque standard).
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

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow n'est pas installé.")

for flux in (sys.stdout, sys.stderr):
    if hasattr(flux, "reconfigure"):
        flux.reconfigure(encoding="utf-8", errors="replace")

BUCKET = "photos-plats"
IMAGES = modele.RACINE / "images"

# Le format des photos de plats du site. Les plus anciennes sont en 900 × 675 ;
# on monte à 1200 × 900 pour les écrans à forte densité, en gardant le 4:3 qui
# structure toute la carte.
LARGEUR, HAUTEUR = 1200, 900


def appel(base: str, cle: str, chemin: str, methode: str = "GET",
          corps: dict | None = None, brut: bool = False):
    requete = urllib.request.Request(
        f"{base}/storage/v1/{chemin}", method=methode,
        data=json.dumps(corps).encode() if corps is not None else None,
        headers={"Authorization": f"Bearer {cle}", "apikey": cle,
                 **({"Content-Type": "application/json"} if corps is not None else {})})
    try:
        with urllib.request.urlopen(requete, timeout=60) as reponse:
            donnees = reponse.read()
            return donnees if brut else json.loads(donnees.decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:200]
        raise SystemExit(f"Storage a refusé « {chemin} » ({e.code}) : {detail}")
    except urllib.error.URLError as e:
        raise SystemExit(f"Storage injoignable : {e.reason}")


def au_format(donnees: bytes) -> Image.Image:
    """Recadre au centre en 4:3 et redimensionne.

    Un recadrage centré n'est pas toujours le meilleur cadrage, mais c'est le
    seul choix raisonnable sans intervention humaine — et Karine voit le
    résultat sur le site, elle peut reprendre la photo.
    """
    import io
    image = Image.open(io.BytesIO(donnees))
    image = image.convert("RGB")

    # Les photos de téléphone portent une orientation dans leurs métadonnées :
    # sans cela, une photo prise à la verticale arriverait couchée.
    try:
        from PIL import ImageOps
        image = ImageOps.exif_transpose(image)
    except Exception:
        pass

    vise = LARGEUR / HAUTEUR
    l, h = image.size
    if l / h > vise:
        neuve = int(h * vise)
        gauche = (l - neuve) // 2
        image = image.crop((gauche, 0, gauche + neuve, h))
    else:
        neuve = int(l / vise)
        haut = (h - neuve) // 2
        image = image.crop((0, haut, l, haut + neuve))

    return image.resize((LARGEUR, HAUTEUR), Image.LANCZOS)


def main() -> int:
    base = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
    cle = os.environ.get("SUPABASE_SERVICE_KEY") or ""
    if not base or not cle:
        raise SystemExit("SUPABASE_URL et SUPABASE_SERVICE_KEY doivent être "
                         "définies dans l'environnement.")

    fichiers = appel(base, cle, f"object/list/{BUCKET}", "POST",
                     {"prefix": "", "limit": 200,
                      "sortBy": {"column": "name", "order": "asc"}})
    noms = [f["name"] for f in fichiers if f.get("name")]
    if not noms:
        print("  Aucune photo en attente.")
        return 0

    # Un fichier dont le nom ne correspond à aucun plat n'a rien à faire dans
    # le dépôt : on le laisse dans le bucket plutôt que de le publier.
    carte = modele.lire("carte")
    slugs = {p["slug"] for cle_liste, _ in modele.FAMILLES for p in carte[cle_liste]}

    traitees, ignorees = [], []
    for nom in noms:
        slug = Path(nom).stem
        if slug not in slugs:
            ignorees.append(nom)
            continue
        donnees = appel(base, cle, f"object/{BUCKET}/{nom}", brut=True)
        cible = IMAGES / f"{slug}.jpg"
        au_format(donnees).save(cible, quality=88, optimize=True, progressive=True)
        taille = cible.stat().st_size / 1024
        print(f"  ✓ {slug}.jpg  {LARGEUR}×{HAUTEUR}  {taille:.0f} Ko")
        traitees.append(nom)

    if traitees:
        appel(base, cle, f"object/{BUCKET}", "DELETE", {"prefixes": traitees})
        print(f"  Bucket vidé ({len(traitees)} fichier(s)).")

    for nom in ignorees:
        print(f"  ! « {nom} » ne correspond à aucun plat : laissé dans le bucket.")

    # Le workflow s'en sert pour ne relancer l'optimiseur d'images que lorsque
    # c'est utile : sans photo, rien à recalculer.
    sortie = os.environ.get("GITHUB_OUTPUT")
    if sortie:
        with open(sortie, "a", encoding="utf-8") as f:
            f.write(f"photos={'oui' if traitees else 'non'}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
