# Les photos du site

Déposez simplement les fichiers dans ce dossier, avec le bon nom.
Tant qu'un fichier n'existe pas, le site affiche un aplat coloré portant le nom
du plat — rien ne casse, rien n'apparaît en erreur.

> **Après avoir ajouté ou remplacé une photo, lancez :**
>
> ```bash
> python3 outils/optimiser-images.py
> ```
>
> Le script fabrique à côté de chaque `.jpg` une version `.avif` et une version
> `.webp`, deux à trois fois plus légères, que les navigateurs récents utilisent
> à la place. Les fichiers `-900`, `-1400` et `-1800` sont les versions réduites
> des grandes images d'ambiance, pour les téléphones. Tout cela se produit tout
> seul : vous ne déposez que le `.jpg`.
>
> Ne modifiez pas les `.avif` et `.webp` à la main, ils sont réécrits à chaque
> passage du script.

## Format

- **JPEG** (`.jpg`), pas de PNG pour les photos : cinq fois plus lourd.
- **1200 × 900 pixels** environ suffisent largement. Inutile de mettre du 6000 px.
- Visez **moins de 300 Ko par photo**. Au-delà, le site devient lent sur mobile,
  et Google le sanctionne.
- Cadrage **paysage** (plus large que haut) pour les plats.

## Noms de fichiers attendus

### Bannière et pages

| Fichier | Où il apparaît |
|---|---|
| `accueil.jpg` | Grande photo de fond de la page d'accueil. Prenez la plus belle : un buffet dressé, une table garnie. Elle est assombrie, le détail importe moins que l'ambiance. |
| `karine.jpg` | Section « Depuis 2009 » de l'accueil. Karine sur son stand, de préférence en train de travailler. |
| `stand.jpg` | Page Marchés. Le stand installé, vu d'assez loin. |
| `partage.jpg` | Vignette affichée quand quelqu'un partage le lien sur Facebook ou WhatsApp. Format 1200 × 630. |

### Plats

Le nom du fichier reprend le nom court du plat, tel qu'affiché dans
`admin.html` (onglet Plats, dernière ligne de chaque fiche).

| Fichier | Plat |
|---|---|
| `rougail-saucisses.jpg` | Rougail saucisses |
| `rougail-morue.jpg` | Rougail morue |
| `cari-poulet.jpg` | Cari poulet |
| `poulet-massale.jpg` | Poulet massalé |
| `poulet-coco.jpg` | Poulet coco |
| `poulet-ananas.jpg` | Poulet ananas |
| `poulet-colombo.jpg` | Poulet colombo |
| `curry-dinde.jpg` | Curry de dinde |
| `porc-colombo.jpg` | Porc colombo |
| `porc-ananas.jpg` | Porc ananas |
| `lentilles-boucane.jpg` | Lentilles boucané |
| `boeuf-massale.jpg` | Bœuf massalé |
| `cari-agneau.jpg` | Cari d'agneau |
| `cari-poisson-crevettes.jpg` | Cari poisson ou crevettes |
| `crevettes-coco.jpg` | Crevettes coco |
| `samoussas.jpg` | Samoussas |
| `accras-morue.jpg` | Accras de morue |
| `bouchons.jpg` | Bouchons |
| `punch-planteur.jpg` | Punch planteur |

**Priorité si vous n'avez pas le temps de tout faire :** `accueil.jpg`,
`rougail-saucisses.jpg`, `samoussas.jpg`, `crevettes-coco.jpg`, `karine.jpg`.
Ce sont celles qu'on voit en premier.

## Conseils de prise de vue

- **À la lumière du jour**, près d'une fenêtre, jamais au flash : le flash écrase
  les couleurs et fait briller la sauce d'une façon peu appétissante.
- **De trois quarts ou de haut**, pas de face.
- Une **assiette blanche** ou un plat sombre : le fond neutre met la couleur du
  cari en valeur.
- Remplissez le cadre. Une petite assiette perdue au milieu d'une grande table
  ne donne envie à personne.

## Le logo

`logo.png`, `logo-blanc.png` et leurs versions `@2x` ont été reconstruits à
partir du PDF de référence. Ils sont **de qualité limitée** (l'original du PDF
faisait 213 × 161 pixels). Si vous retrouvez le fichier d'origine du logo
(`.ai`, `.eps`, `.svg` ou un grand PNG), remplacez-les : le rendu sera bien plus
net, surtout sur les écrans récents.
