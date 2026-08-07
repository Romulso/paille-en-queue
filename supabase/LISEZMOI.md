# Phase 1 — mise en route

Suite de `CDC-BACKOFFICE.md`. Cette phase se termine quand Karine se connecte
et voit ses 22 produits et ses 5 marchés.

Tout ce qui suit se fait **une fois**. Le code, lui, est déjà écrit et vérifié.

---

## Ce qui est déjà fait

| Fichier | Rôle |
|---|---|
| `supabase/schema.sql` | Les six tables, les contraintes, RLS et ses politiques |
| `supabase/donnees-initiales.sql` | Les données actuelles du site, prêtes à importer |
| `outils/modele.py` | Les règles de traduction JSON ↔ base, partagées par les scripts |
| `outils/generer-seed-supabase.py` | Reconstruit `donnees-initiales.sql` depuis `data/*.json` |
| `outils/verifier-modele.py` | Prouve que le passage par la base ne perd rien |
| `backoffice.html` | Connexion et affichage en lecture seule |

La fidélité du modèle est vérifiable sans base ni réseau :

```
python outils/verifier-modele.py
```

Il doit afficher « Aucune différence ». Si un jour il ne le fait plus, c'est
qu'une modification a rendu l'export infidèle : à corriger avant de publier.

---

## Les cinq étapes

### 1 · Créer le projet Supabase

Sur [supabase.com](https://supabase.com), un projet dans la région
**Europe (Paris ou Francfort)** — les données restent dans l'Union.

Noter le mot de passe de la base dans un gestionnaire de mots de passe : il
n'est plus affiché ensuite.

> Le compte doit survivre au projet. Une adresse partagée et durable vaut mieux
> qu'une adresse personnelle (question 2 du § 10 du cahier des charges).

### 2 · Créer les tables

**SQL Editor → New query.** Coller le contenu entier de `supabase/schema.sql`,
exécuter.

Puis vérifier, avec la requête laissée en commentaire à la fin du fichier :
les six tables doivent apparaître avec `rls_active = t` **et** `politiques = 1`.
Une table à zéro politique ne renverra jamais aucune ligne, sans jamais dire
pourquoi.

### 3 · Importer les données

Même écran, nouvelle requête. Coller `supabase/donnees-initiales.sql`,
exécuter. Le compte attendu est rappelé en commentaire à la fin :

```
produits 22 · menus 3 · lignes de menu 28 · marchés 5 · avis 1
```

### 4 · Créer les deux comptes

**Authentication → Users → Add user → Create new user.** Deux comptes, e-mail
et mot de passe, en cochant « Auto Confirm User ».

Pas d'inscription ouverte : dans **Authentication → Sign In / Providers**,
laisser « Allow new users to sign up » désactivé. À deux utilisateurs, une
inscription ouverte n'est qu'une porte de plus.

### 5 · Raccorder le backoffice

> **Déjà fait** pour le projet `ktdlmdidtfptkudrnyzi`. À refaire seulement si
> le projet change.

**Project Settings → API Keys**, puis reporter dans `backoffice.html`, bloc
`RÉGLAGES` en bas du fichier :

- `Project URL` → `SUPABASE_URL`
- clé **publishable** (autrefois « anon ») → `SUPABASE_ANON`

Ces deux valeurs sont publiables — c'est le sens du mot. Sans compte, elles ne
donnent accès à rien, puisque RLS ferme les six tables.

> ⛔ La clé **secret** (autrefois « service_role ») ne doit **jamais** figurer
> dans ce fichier ni dans aucun autre fichier du dépôt. Elle contourne RLS.
> Elle ne servira qu'en phase 3, dans les secrets GitHub Actions.

Tant que les deux valeurs sont vides, `backoffice.html` affiche ces
instructions au lieu d'un écran cassé.

---

## Vérifier

Ouvrir `backoffice.html`, se connecter, et comparer avec le site :

- **Marchés** : 5 lignes, Le Pizou le mardi jusqu'au 31 août ;
- **Carte** : 15 plats, 3 entrées, 1 boisson, 3 suppléments ;
- **Menus** : 3 menus, le Lagon à « 24 € à 26 € » ;
- **Réglages** : le téléphone, et le bloc « Gabarits » dépliable.

Si une table s'affiche vide sans message d'erreur, c'est RLS sans politique.
C'est le piège du § 5, et il ne se signale pas autrement.

---

## Ce que la phase 1 ne fait pas

Rien n'écrit dans la base depuis le backoffice, et rien ne publie. Le contenu
du site continue de se modifier par `admin.html`, comme avant. Supabase et le
site vivent côte à côte sans se parler — c'est voulu : tant que la phase 3
n'existe pas, la base n'est qu'une copie.

---

# Phase 3 — la publication

Karine modifie dans le backoffice, qui écrit dans Supabase. Un workflow GitHub
va chercher la base toutes les quinze minutes, réécrit `data/*.json`, régénère
le site et le PDF, puis pousse. GitHub Pages republie derrière.

Le site public reste entièrement statique : il n'interroge jamais Supabase.
Si la base tombe, le site ne s'en aperçoit pas.

## Ce qu'il reste à faire, une fois

Déposer la clé secrète dans les secrets du dépôt :

1. **Supabase → Project Settings → API Keys**, copier la clé **secret**
   (autrefois `service_role`).
2. **GitHub → Settings → Secrets and variables → Actions → New repository
   secret**, nom exact `SUPABASE_SERVICE_KEY`.

> ⛔ Cette clé contourne RLS. Elle ne doit jamais être collée dans un fichier
> du dépôt, ni dans une conversation. Les secrets GitHub ne sont pas lisibles
> après enregistrement, même par vous : c'est normal.

Tant que le secret est absent, le workflow s'arrête proprement avec un
avertissement, sans envoyer de mail d'erreur.

## Le premier essai

**Actions → Publier le site → Run workflow**, en cochant
**« Comparer sans rien écrire ni pousser »**.

L'export doit annoncer « Aucune différence : l'export est fidèle ». C'est la
vérification du § 9 du cahier des charges, exécutée sur les vraies données :
elle prouve que le passage par la base ne modifie rien.

Si des différences apparaissent, ne pas lancer la publication réelle : les
regarder d'abord.

## Le délai

Le cron est traité « au mieux » par GitHub : comptez quinze à trente minutes,
plus une à deux minutes de construction Pages. Pour publier tout de suite,
relancer le workflow à la main sans cocher la case.

## Ce qui protège

`outils/exporter-supabase.py` refuse d'écrire si la base renvoie moins de
5 produits, moins d'un menu ou des gabarits vides. Une base vidée par accident
ne peut donc pas remplacer le site par une coquille vide.
