# Le Paille en Queue

Site vitrine du **Paille en Queue**, traiteur créole et réunionnais en Dordogne
depuis 2009. Repas livrés à partir de 10 parts, buffets et prestations
événementielles pour les entreprises, les communes, les associations et les
particuliers.

🌐 **<https://romulso.github.io/paille-en-queue/>**

## Comment c'est fait

HTML, CSS et JavaScript, sans framework ni étape de compilation. Le contenu qui
change souvent vit dans `data/*.json` et s'édite depuis une page privée,
`admin.html`.

- Aucune dépendance, aucun `node_modules`, aucun abonnement
- Aucun cookie, aucun traceur, aucune ressource externe
- Deux polices variables auto-hébergées (99 Ko en tout)
- Hébergement GitHub Pages

## Structure

```
index.html              Accueil
carte.html              15 plats, entrées, buffet, 3 menus
evenements.html         Entreprises, communes, associations, familles
marches.html            Calendrier des marchés
devis.html              Formulaire de demande de devis
faq.html                13 questions fréquentes
mentions-legales.html   Mentions légales et RGPD
admin.html              Édition du contenu (non référencé, exclu de Google)

style.css               Mise en forme
site.js                 Comportements
data/                   Contenu éditable (carte, marchés, avis, réglages)
images/                 Logo et photos — voir images/LISEZ-MOI.md
fonts/                  Fraunces et Outfit — voir fonts/LISEZ-MOI.md
```

## Voir le site en local

```bash
python3 -m http.server 8777
```

Puis <http://localhost:8777>. Un vrai serveur est nécessaire : ouvrir les
fichiers par double-clic empêche le chargement de `data/*.json`.

## Aller plus loin

Tout est expliqué dans **[GUIDE.md](GUIDE.md)** : publication, nom de domaine,
branchement du formulaire de devis, modification du contenu, ajout des photos,
et la liste de ce qui reste à compléter.
