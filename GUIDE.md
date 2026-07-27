# Le Paille en Queue — guide du site

Site vitrine du Paille en Queue, traiteur créole en Dordogne.
HTML, CSS et JavaScript classiques : **aucun logiciel à installer, aucune
compilation, aucun abonnement**. Le contenu qui change souvent vit dans des
fichiers du dossier `data/`, modifiables depuis `admin.html`.

---

## 1 · Ce qu'il y a dans le dossier

| Fichier | Rôle |
|---|---|
| `index.html` | Page d'accueil |
| `carte.html` | Les 15 plats, les entrées, le buffet et les 3 menus |
| `evenements.html` | Entreprises, communes, associations, fêtes de famille |
| `marches.html` | Calendrier des marchés |
| `devis.html` | Formulaire de demande de devis |
| `faq.html` | Questions fréquentes |
| `mentions-legales.html` | Mentions légales et RGPD |
| `admin.html` | **Page privée** d'édition du contenu |
| `style.css` | Toute la mise en forme |
| `site.js` | Les comportements (menus, filtres, formulaire) |
| `data/*.json` | Le contenu modifiable |
| `images/` | Logo et photos — voir `images/LISEZ-MOI.md` |

---

## 2 · Voir le site sur son ordinateur

Le site lit ses données avec `fetch`, ce qu'un navigateur refuse quand on
ouvre un fichier par double-clic. Il faut un petit serveur local. macOS a tout
ce qu'il faut :

```bash
cd /Users/admin/Projets/paille-en-queue && python3 -m http.server 8777
```

Puis ouvrez <http://localhost:8777>. Pour arrêter : `Ctrl + C`.

---

## 3 · Mettre le site en ligne

Le site est publié sur **GitHub Pages**, comme `studio-saint-lary`.

- Dépôt : <https://github.com/Romulso/paille-en-queue>
- Adresse publique : <https://romulso.github.io/paille-en-queue/>

Pour publier une modification :

```bash
cd /Users/admin/Projets/paille-en-queue
git add -A && git commit -m "Décrire la modification"
git push
```

Une à deux minutes plus tard, le site en ligne est à jour.

### Plus tard : le nom de domaine

Comptez ~10 €/an chez OVH, Gandi ou Ionos. `lepailleenqueue.fr` est le choix
évident. Dans la zone DNS du domaine :

| Type | Nom | Valeur |
|---|---|---|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | `romulso.github.io.` |

Puis **Settings → Pages → Custom domain**, saisir le domaine, et cocher
« Enforce HTTPS » dès que la case devient active.

> **Important :** le jour où le domaine est branché, il faut remplacer
> `https://romulso.github.io/paille-en-queue/` par la nouvelle adresse partout où
> elle apparaît — balises `canonical` et `og:url` des sept pages, `robots.txt`
> et `sitemap.xml`. Une seule commande suffit :
>
> ```bash
> grep -rl "romulso.github.io/paille-en-queue/" . | xargs sed -i '' 's|https://romulso.github.io/paille-en-queue/|https://lepailleenqueue.fr/|g'
> ```
>
> Tant que ce n'est pas fait, Google continue d'indexer l'ancienne adresse.

---

## 4 · Recevoir les demandes de devis

**En l'état, le formulaire fonctionne déjà** : à l'envoi, il ouvre le logiciel
de messagerie du visiteur avec un message pré-rempli et bien présenté. C'est
fiable, mais tout le monde n'a pas de messagerie configurée sur son téléphone,
et une partie des demandes se perd.

Pour recevoir les demandes directement par e-mail, il faut un petit service
intermédiaire. **Formspree** est le plus simple et gratuit jusqu'à
50 demandes par mois :

1. Créer un compte sur <https://formspree.io> avec l'adresse de Karine
   (**cette étape doit être faite par vous** : elle demande de choisir un mot
   de passe et de confirmer l'adresse e-mail).
2. Créer un formulaire, appelé par exemple « Devis site ». Formspree donne une
   adresse du type `https://formspree.io/f/xxxxxxxx`.
3. Ouvrir `admin.html`, onglet **Réglages**, coller cette adresse dans le champ
   « Adresse d'envoi du formulaire de devis », puis **Télécharger config.json**
   et remplacer `data/config.json`.
4. Remettre le site en ligne (`git add -A && git commit -m "Formulaire branché"
   && git push`). Terminé — chaque demande arrive par e-mail, proprement
   formatée.
5. Envoyer une demande de test depuis le site : Formspree demande de confirmer
   la première réception en cliquant sur un lien dans l'e-mail.

Le tout premier envoi peut arriver dans les indésirables : marquez-le comme
« non indésirable » une fois pour toutes.

**Web3Forms** (<https://web3forms.com>, gratuit jusqu'à 250 demandes/mois) est
une alternative sans création de compte. Il faut alors renseigner deux lignes :

```json
"formulaireEndpoint": "https://api.web3forms.com/submit",
"formulaireChampsCaches": { "access_key": "la-cle-reçue-par-mail" },
```

---

## 5 · Modifier le contenu

Ouvrir `admin.html` **depuis le site en ligne** (ou depuis le serveur local de
l'étape 2). Quatre onglets :

- **Marchés** — ajouter, modifier, supprimer les marchés. Tant que la liste est
  vide, la page invite à téléphoner.
- **Avis clients** — les témoignages. La section reste masquée tant qu'il n'y en
  a aucun. **N'y mettre que de vrais avis** : un faux témoignage est une
  pratique commerciale trompeuse, sanctionnée par la loi.
- **Plats** — nom, prix, description, mise en avant sur l'accueil.
- **Menus** — les trois formules.

Une fois les modifications faites, cliquer sur **Télécharger** en bas du
panneau, remplacer le fichier correspondant dans `data/`, et remettre le site
en ligne. Rien n'est publié avant cette étape : on peut donc essayer sans
crainte.

---

## 6 · Ajouter les photos

Tout est expliqué dans `images/LISEZ-MOI.md` : noms de fichiers attendus,
formats, et conseils de prise de vue. En résumé : des `.jpg` d'environ
1200 × 900 pixels, moins de 300 Ko, à la lumière du jour.

Tant qu'une photo manque, le site affiche un aplat coloré avec le nom du plat.
Ce n'est pas une erreur, et rien ne casse.

---

## 7 · Les règles commerciales affichées sur le site

Ces informations sont écrites en clair dans le HTML (pour le référencement) et
répétées dans `data/carte.json`, qui les rafraîchit si elles changent. Pour en
modifier une, cherchez la phrase dans les fichiers et changez les deux endroits.

| Règle | Valeur affichée |
|---|---|
| Commande minimum | 10 parts |
| Délai de commande | 4 à 5 jours avant la date |
| Zone de livraison | 30 km autour de Montpeyroux |
| Frais de livraison | 5 € jusqu'à 10 km, 10 € au-delà |
| Cuisine sur place | à partir de 50 convives |
| Jamais compris | le service, la vaisselle et le pain |
| Pain | 1 € par personne |
| Vaisselle | 0,40 € par personne — assiettes et couverts carton et bois |
| Service à table | sur devis, selon la durée et le nombre de convives |
| Supplément menus | +2 € pour un plat poisson, crevettes ou morue |
| Acompte | 30 % à la signature, solde à la livraison |
| Validité du devis | 1 mois |

> **À vérifier :** le PDF de référence mentionnait « boule de pain comprise »
> dans le menu à 24/26 € et « pain compris » dans celui à 28/30 €. Le pain ayant
> été retiré des prix, ces deux lignes ont été supprimées des menus. Si le pain
> doit rester compris dans ces deux formules, il faut les rétablir.

---

## 8 · Ce qui reste à compléter

- [ ] **Les photos** — c'est ce qui manque le plus au site aujourd'hui.
- [ ] **Le logo en haute définition** — celui du PDF fait 213 × 161 pixels.
- [ ] **Le nom de domaine**, puis la mise à jour des URL (section 3).
- [ ] **Le service d'envoi du formulaire** (section 4).
- [ ] **Les marchés** — communes, jours et horaires, à saisir dans `admin.html`.
- [ ] **Le médiateur de la consommation** — obligatoire à mentionner pour toute
      vente aux particuliers (article L.616-1 du code de la consommation).
      Adhésion ~30 €/an. À ajouter dans les mentions légales.
- [ ] **La TVA** — si l'entreprise y est assujettie, ajouter le numéro de TVA
      intracommunautaire aux mentions légales.
- [ ] **Une adresse e-mail au nom du domaine** — `contact@lepailleenqueue.fr`
      inspire plus confiance aux mairies et aux entreprises que le Gmail actuel,
      dont le suffixe « 33 » évoque en plus la Gironde et non la Dordogne.
- [ ] **Trois vrais avis clients** — à demander à des clients récents.
- [ ] **La fiche Google Business Profile** — gratuite, et de loin le meilleur
      levier pour être trouvé sur « traiteur réunionnais Dordogne ».
