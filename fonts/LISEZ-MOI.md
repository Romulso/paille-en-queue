# Les polices du site

Deux polices variables, auto-hébergées : aucun appel à un serveur extérieur,
donc rien à déclarer côté RGPD et rien qui ralentisse l'affichage.

| Fichier | Police | Usage | Poids |
|---|---|---|---|
| `Fraunces-var.woff2` | [Fraunces](https://fonts.google.com/specimen/Fraunces) | Titres | 67 Ko |
| `Outfit-var.woff2` | [Outfit](https://fonts.google.com/specimen/Outfit) | Textes courants | 32 Ko |

Les deux sont sous **SIL Open Font License 1.1**, qui autorise l'usage
commercial et l'hébergement sur son propre site.

Sous-ensemble « latin » uniquement (U+0000–00FF plus l'œ et l'euro) : tous les
caractères du français sont couverts, sans embarquer les alphabets qui ne
serviront jamais.

Si un fichier est supprimé, le site ne casse pas : il retombe sur Georgia pour
les titres et sur la police système pour le reste (voir `--titre` et `--sans`
dans `style.css`).
