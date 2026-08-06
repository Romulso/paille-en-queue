# Cahier des charges — backoffice du Paille en Queue

> Document de cadrage. Projet d'apprentissage encadré : l'objectif est autant
> de monter en compétence sur Supabase, SQL et l'intégration continue que de
> livrer l'outil. Le périmètre est volontairement resserré.

---

## 1 · Pourquoi ce projet

### Ce qui ne va pas aujourd'hui

Le contenu du site vit dans `data/*.json` et s'édite depuis `admin.html`. Pour
publier une modification, il faut aujourd'hui :

1. ouvrir `admin.html`, modifier, cliquer sur « Télécharger » ;
2. retrouver le fichier téléchargé et le déplacer dans `data/` ;
3. lancer `python outils/generer-html.py` ;
4. lancer `python outils/generer-menu-pdf.py` si les prix ont changé ;
5. `git add`, `git commit`, `git push`.

**Karine ne peut pas faire cette chaîne seule.** Chaque changement de marché ou
de prix passe donc par un développeur. C'est le vrai coût, pas le volume de
données.

Trois autres faiblesses, par ordre de gravité :

| Problème | Conséquence |
|---|---|
| `admin.html` n'a **aucune authentification** | La page n'est protégée que par le fait qu'aucun lien n'y mène. Elle est publiquement accessible à qui connaît l'adresse. |
| L'étape 3 peut être oubliée | Le site reste affiché correctement pour les visiteurs, mais les moteurs de recherche continuent de voir l'ancienne carte. Panne silencieuse. |
| Pas d'historique lisible | Revenir en arrière suppose de manipuler git. |

### Ce que le backoffice doit apporter

Dans l'ordre de valeur :

1. **Publier sans développeur.** Karine modifie, clique sur « Publier », le site
   se met à jour tout seul.
2. **Fermer la porte.** Un identifiant et un mot de passe.
3. **Travailler depuis un téléphone.** Les marchés se décident souvent la veille.

---

## 2 · La contrainte à ne jamais casser

**Le site doit rester entièrement statique.**

Le contenu du site a été rendu visible pour les moteurs de recherche au prix
d'un travail spécifique : `outils/generer-html.py` recopie les données dans le
HTML, parce qu'un robot qui n'exécute pas JavaScript ne voyait qu'une page vide.
Le site est passé de « jamais exploré par Google » à cinq pages indexées et une
première place sur « traiteur créole dordogne ».

> ⛔ **Interdit : que le site public interroge Supabase depuis le navigateur.**
> Ce serait exactement le défaut corrigé, en pire — avec en plus une dépendance
> à un service tiers pour afficher la carte.

### L'architecture qui respecte cette contrainte

```
   Karine                Backoffice            Supabase           GitHub
   ──────                ──────────            ────────           ──────
   modifie   ─────────►  écrit dans   ───────► base de   
   un prix               la base               données

   clique
   « Publier » ────────────────────────────────────────────►  déclenche
                                                              une action

                                                    ┌─────────────────────┐
                                                    │ 1. lit Supabase     │
                                                    │ 2. écrit data/*.json│
                                                    │ 3. generer-html.py  │
                                                    │ 4. generer-menu-pdf │
                                                    │ 5. commit + push    │
                                                    └──────────┬──────────┘
                                                               ▼
                                                    GitHub Pages republie
                                                    le site, 100 % statique
```

**Supabase devient la source de vérité. `data/*.json` devient un artefact de
build.** Tout ce qui existe en aval — les quatre scripts Python, le HTML généré,
le PDF — continue de fonctionner sans être modifié.

Conséquences agréables :

- si Supabase tombe, **le site public ne s'en aperçoit pas** ;
- l'historique git reste lisible : chaque publication est un commit ;
- on peut revenir en arrière avec `git revert`, sans toucher à la base.

---

## 3 · Périmètre

### Dans le périmètre

| Ce que Karine doit pouvoir faire | Depuis |
|---|---|
| Ajouter, modifier, supprimer un plat, une entrée, une boisson, un supplément | téléphone ou ordinateur |
| Modifier les trois menus et leur composition | ordinateur |
| Gérer les marchés (hebdomadaires et dates uniques) | téléphone |
| Saisir et publier un avis client | ordinateur |
| Modifier les réglages (téléphone, tarifs de livraison, liens) | ordinateur |
| Publier — c'est-à-dire mettre le site à jour | un bouton |
| Se connecter, se déconnecter | — |

### Hors périmètre — à ne pas faire

Écrire ce qu'on ne fait **pas** est la partie la plus utile d'un cahier des
charges. Chacun de ces points est un piège classique de premier projet :

- **Les images.** Elles restent dans git et passent par
  `outils/optimiser-images.py`. Supabase Storage est un sujet à part entière,
  il viendra plus tard ou jamais.
- **`data/zone.json`.** C'est un fichier calculé par `outils/calculer-zone.py`,
  pas du contenu éditable. Il n'a rien à faire dans une base.
- **Les rôles et permissions fines.** Deux personnes utiliseront cet outil. Un
  seul niveau d'accès suffit.
- **Un éditeur de texte riche.** Les descriptions sont des phrases simples. Un
  `<textarea>` fait le travail.
- **Un aperçu en direct.** `apercu.html` existe déjà.
- **Le multilingue, les brouillons, les versions programmées.** Non.
- **Un framework front.** Le site n'a aucune étape de compilation et n'en aura
  pas. Le backoffice sera du HTML, du CSS et du JavaScript, comme le reste.

### Le cas des réglages

`data/config.json` contient une quarantaine de champs, dont certains sont des
réglages techniques (adresse d'envoi du formulaire, champs cachés de la
newsletter). Ils n'ont pas vocation à être modifiés par Karine.

**Proposition :** deux onglets distincts dans le backoffice — « Réglages » pour
les six champs qu'elle touche réellement (téléphone, e-mail, liens sociaux,
chiffres d'avis), et « Avancé » pour le reste, sous un avertissement.

---

## 4 · Modèle de données

Six tables. Le point pédagogique important : **`carte.json` sépare aujourd'hui
`plats`, `entrees`, `boissons` et `supplements` en quatre listes, alors que ce
sont les mêmes objets.** En base, c'est une seule table avec une colonne
`famille`. C'est la première leçon de normalisation du projet.

```sql
-- ---------------------------------------------------------------
-- Ce que l'on vend, à la part
-- ---------------------------------------------------------------
create type famille_produit as enum ('plat', 'entree', 'boisson', 'supplement', 'buffet');
create type categorie_plat  as enum ('volaille', 'porc', 'boeuf-agneau', 'mer', 'autre');

create table produits (
  id           uuid primary key default gen_random_uuid(),
  famille      famille_produit not null,
  slug         text not null unique,      -- sert au nom du fichier photo
  nom          text not null,
  description  text not null default '',
  prix         numeric(6,2),              -- null = « sur devis »
  unite        text,                      -- « la part », « les 16 », « la pièce »
  categorie    categorie_plat,            -- seulement pour famille = 'plat'
  vedette      boolean not null default false,
  ordre        integer not null default 0,
  actif        boolean not null default true,
  modifie_le   timestamptz not null default now()
);

-- ---------------------------------------------------------------
-- Les menus, et leur composition
-- ---------------------------------------------------------------
create table menus (
  id                 uuid primary key default gen_random_uuid(),
  slug               text not null unique,
  nom                text not null,
  resume             text not null default '',
  prix               numeric(6,2) not null,
  prix_max           numeric(6,2),          -- null si prix unique
  supplement_motif   text,                  -- « avec un plat poisson… »
  ordre              integer not null default 0,
  actif              boolean not null default true,
  modifie_le         timestamptz not null default now()
);

create type bloc_menu as enum ('entree', 'plat', 'dessert', 'inclus');

-- Une ligne par élément : c'est la relation un-à-plusieurs du projet.
create table menu_lignes (
  id       uuid primary key default gen_random_uuid(),
  menu_id  uuid not null references menus(id) on delete cascade,
  bloc     bloc_menu not null,
  libelle  text not null,
  ordre    integer not null default 0
);

-- ---------------------------------------------------------------
-- Les marchés
-- ---------------------------------------------------------------
create type type_marche as enum ('matin', 'nocturne');

create table marches (
  id         uuid primary key default gen_random_uuid(),
  lieu       text not null,
  jour       text not null,        -- « mardi » … ou « 2026-12-14 » pour une date unique
  type       type_marche not null default 'matin',
  horaire    text default '',
  precision  text default '',
  jusquau    date,                 -- null = pas de fin de saison
  ordre      integer not null default 0,
  actif      boolean not null default true
);

-- ---------------------------------------------------------------
-- Les avis
-- ---------------------------------------------------------------
create table avis (
  id         uuid primary key default gen_random_uuid(),
  auteur     text not null,        -- prénom + initiale, jamais le nom complet
  note       smallint check (note between 1 and 5),
  contexte   text default '',      -- « Mariage à Coutras, juin 2026 »
  texte      text not null,
  date_avis  date,
  publie     boolean not null default false,
  ordre      integer not null default 0
);

-- ---------------------------------------------------------------
-- Les réglages : une seule ligne, verrouillée
-- ---------------------------------------------------------------
create table reglages (
  id                      boolean primary key default true check (id),
  telephone               text not null,
  telephone_lien          text not null,
  email                   text not null,
  ville_affichee          text not null,
  minimum_parts           integer not null default 10,
  frais_livraison_proche  numeric(6,2) not null default 5,
  frais_livraison_loin    numeric(6,2) not null default 10,
  rayon_livraison_km      integer not null default 50,
  facebook                text default '',
  instagram               text default '',
  google_business_profile text default '',
  avis_google_note        text default '',
  avis_google_nombre      text default '',
  avis_facebook_taux      text default '',
  avis_facebook_nombre    text default '',
  abonnes_facebook        text default '',
  modifie_le              timestamptz not null default now()
);
```

> `id boolean primary key default true check (id)` est une astuce classique :
> elle garantit qu'il ne peut exister **qu'une seule ligne** de réglages.
> Comprendre pourquoi cela fonctionne est un bon exercice.

### Ce qui reste en JSON

Les mentions commerciales de `carte.json` (`mentionPart`, `mentionMinimum`,
`mentionLivraison`…) et les champs techniques de `config.json` peuvent rester
dans un `jsonb` de la table `reglages` pour la première version. Les modéliser
proprement n'apporte rien tant que personne ne les édite.

---

## 5 · Sécurité

C'est la partie où l'on apprend le plus, et celle qu'on rate le plus souvent.

### Le principe qui simplifie tout

**Le site public ne lit jamais Supabase.** Il lit du HTML statique. Personne
d'autre que Karine et Romu n'a donc besoin d'accéder à la base.

Cela permet une règle simple et stricte : **tout est fermé, sauf aux personnes
connectées.** Pas de politique de lecture publique, pas d'anonymisation, pas de
données exposées par erreur.

```sql
-- À faire sur les six tables, sans exception.
alter table produits    enable row level security;
alter table menus       enable row level security;
alter table menu_lignes enable row level security;
alter table marches     enable row level security;
alter table avis        enable row level security;
alter table reglages    enable row level security;

-- Une seule politique par table : les utilisateurs connectés font tout.
create policy "connectes: tout" on produits
  for all
  to authenticated
  using (true)
  with check (true);
-- … à répéter pour les cinq autres tables.
```

> **Piège classique :** activer RLS *sans* créer de politique rend la table
> muette — aucune erreur, juste zéro ligne renvoyée. On y perd tous une soirée.

### Les clés

Supabase fournit deux clés. Confondre les deux est la faute qui expose une base.

| Clé | Où elle va | Ce qu'elle peut |
|---|---|---|
| `anon` (publiable) | dans le JavaScript du backoffice | rien sans connexion — RLS s'applique |
| `service_role` (secrète) | **uniquement** dans les secrets GitHub Actions | contourne RLS, lit tout |

> ⛔ La clé `service_role` ne doit **jamais** apparaître dans un fichier du
> dépôt, ni dans du code envoyé au navigateur. Si elle fuite, la base est
> ouverte à tous. En cas de doute, la régénérer depuis l'interface Supabase.

### Comptes

Deux comptes créés à la main dans Supabase Auth, e-mail et mot de passe. Pas
d'inscription ouverte, pas de récupération de mot de passe en libre-service —
il y a deux utilisateurs, un message suffit.

---

## 6 · Le backoffice

### Contraintes techniques

- HTML, CSS, JavaScript. **Aucune étape de compilation**, comme le reste du site.
- Le client Supabase se charge depuis un CDN en `<script type="module">`.
- La feuille de style du site est réutilisée : `admin.html` le fait déjà.
- Utilisable sur un écran de téléphone, au moins pour les marchés.

### Où l'héberger

`admin.html` est aujourd'hui servi par GitHub Pages, dans le même dépôt. Le
backoffice peut prendre la même place — il est protégé par l'authentification,
plus par l'obscurité.

Une page, `backoffice.html`, avec :

- un écran de connexion tant que la session est absente ;
- des onglets, comme aujourd'hui : Marchés · Carte · Menus · Avis · Réglages ;
- un bouton **Publier** bien visible, avec l'état de la dernière publication.

### Le bouton « Publier »

C'est la pièce maîtresse, et la seule qui demande un peu de réflexion.

Au clic, le backoffice appelle l'API GitHub pour déclencher un workflow
(`repository_dispatch`). Le jeton GitHub nécessaire **ne peut pas vivre dans le
navigateur** — il serait lisible par n'importe qui.

Deux solutions, à choisir en connaissance de cause :

| Solution | Avantage | Inconvénient |
|---|---|---|
| **Edge Function Supabase** qui détient le jeton et appelle GitHub | propre, le jeton reste secret | une brique de plus à apprendre |
| **Workflow programmé** toutes les 15 minutes, qui republie si la base a changé | rien à sécuriser | jusqu'à 15 min d'attente |

**Recommandation : commencer par le workflow programmé.** C'est plus simple,
cela fonctionne, et l'Edge Function peut arriver en phase 3 quand le reste
tourne. Un délai de quinze minutes sur un site de traiteur n'a aucune
conséquence.

---

## 7 · La chaîne de publication

Un script `outils/exporter-supabase.py` qui lit la base et écrit `data/*.json`,
au format exact attendu par les scripts existants.

**Point critique : ce script ne doit rien changer d'autre.** Son seul travail
est de produire les mêmes fichiers JSON qu'aujourd'hui. Si sa sortie est
identique à l'existant pour des données identiques, tout le reste fonctionne
sans être touché — c'est la façon de vérifier qu'il est correct.

```yaml
# .github/workflows/publier.yml
name: Publier le site

on:
  schedule:
    - cron: '*/15 * * * *'      # toutes les 15 minutes
  workflow_dispatch:             # et à la demande, depuis GitHub

jobs:
  publier:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }

      - run: pip install supabase fpdf2

      - name: Exporter la base vers data/*.json
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
        run: python outils/exporter-supabase.py

      - name: Régénérer le site
        run: |
          python outils/generer-html.py
          python outils/generer-menu-pdf.py

      - name: Committer s'il y a du changement
        run: |
          git config user.name  "Backoffice"
          git config user.email "backoffice@lepaille-en-queue.fr"
          git add -A
          git diff --staged --quiet || git commit -m "Publication depuis le backoffice"
          git push
```

> `git diff --staged --quiet ||` évite de créer un commit vide toutes les quinze
> minutes. Sans cette ligne, l'historique devient illisible en une journée.

---

## 8 · Étapes

Chaque phase se termine par quelque chose qui marche. C'est ce qui fait tenir un
projet d'apprentissage.

### Phase 1 — La base et la lecture

**Objectif :** voir les vraies données du site dans un backoffice, connecté.

- créer le projet Supabase, écrire le schéma SQL, activer RLS ;
- créer les deux comptes ;
- importer les données existantes de `data/*.json` ;
- `backoffice.html` : connexion, déconnexion, et affichage en **lecture seule**.

**Ce qu'on apprend :** SQL, types, clés étrangères, RLS, authentification.
**Terminé quand :** Karine se connecte et voit ses 22 produits et ses 5 marchés.

### Phase 2 — L'écriture

**Objectif :** modifier depuis le backoffice.

- formulaires de création, modification, suppression sur les six tables ;
- réordonner les plats et les menus ;
- validation des saisies (un prix négatif, un slug en double).

**Ce qu'on apprend :** `insert`, `update`, `delete`, contraintes, gestion
d'erreurs.
**Terminé quand :** un marché ajouté dans le backoffice se retrouve en base.

### Phase 3 — La publication

**Objectif :** le site se met à jour tout seul.

- `outils/exporter-supabase.py` ;
- le workflow GitHub Actions ;
- l'affichage de la date de dernière publication dans le backoffice.

**Ce qu'on apprend :** intégration continue, secrets, automatisation.
**Terminé quand :** Karine modifie un prix, attend, et le voit sur le site.

### Phase 4 — Le confort, si le besoin s'en fait sentir

Bouton « Publier maintenant » via Edge Function · photos dans Supabase Storage ·
journal des modifications · retrait de l'ancien `admin.html`.

---

## 9 · Ce qu'il faut savoir avant de commencer

### Sur le coût

L'offre gratuite de Supabase couvre très largement ce projet — les données
tiennent en quelques dizaines de kilo-octets. **Attention cependant :** un
projet gratuit est mis en pause après une semaine sans activité. Le workflow qui
tourne toutes les quinze minutes l'évite naturellement.

### Sur la proportionnalité

Il faut le dire franchement : **Supabase est surdimensionné pour trente
enregistrements.** Un fichier JSON dans git, c'est ce qui existe déjà, et ça
fonctionne.

Ce n'est pas un problème ici : l'objectif annoncé est l'apprentissage, et ces
compétences — modélisation SQL, RLS, authentification, intégration continue —
sont exactement celles qui servent sur un vrai projet. Il faut simplement ne pas
se raconter que la complexité ajoutée est justifiée par le besoin métier. Le
besoin métier, c'est le bouton « Publier ».

### Sur ce qui ne doit pas casser

Une liste de vérification avant chaque mise en production :

- [ ] le site reste servi en HTML statique, sans appel à Supabase ;
- [ ] `python outils/generer-html.py` ne produit aucune différence après export
      (preuve que l'export est fidèle) ;
- [ ] la clé `service_role` n'apparaît nulle part dans le dépôt ;
- [ ] RLS est activé sur les six tables, avec une politique sur chacune ;
- [ ] `sitemap.xml`, les schémas JSON-LD et le PDF sont toujours corrects.

### Sur la méthode de travail avec Claude Code

- avancer phase par phase, sans commencer la suivante avant que la précédente
  fonctionne ;
- demander à comprendre plutôt qu'à recevoir : « explique-moi pourquoi cette
  politique RLS » vaut mieux que « écris-moi le SQL » ;
- committer souvent, avec des messages qui disent pourquoi ;
- se méfier du code qui marche du premier coup sans qu'on sache pourquoi.

---

## 10 · Questions à trancher avant la phase 1

1. **Le backoffice remplace-t-il `admin.html`, ou cohabitent-ils ?**
   Cohabiter pendant les phases 1 et 2 semble prudent — `admin.html` reste le
   moyen de publier tant que la phase 3 n'est pas finie.
2. **Qui possède le projet Supabase ?** Le compte doit survivre au projet.
3. **Faut-il un environnement de test séparé ?** Recommandé dès la phase 2 :
   travailler directement sur la base de production est une mauvaise habitude
   qu'on ne perd plus.
4. **Le délai de quinze minutes est-il acceptable pour Karine ?** Si elle
   modifie un marché le matin même, peut-être pas — auquel cas l'Edge Function
   passe en phase 3.
