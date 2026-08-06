-- ============================================================================
-- Le Paille en Queue — schéma du backoffice
-- ============================================================================
--
-- À exécuter une seule fois, dans l'éditeur SQL de Supabase, avant
-- supabase/donnees-initiales.sql.
--
-- Ce fichier suit CDC-BACKOFFICE.md § 4 et § 5. Cinq écarts, tous motivés en
-- commentaire à l'endroit concerné : cherchez « ÉCART ».
--
-- Le script est ré-exécutable : il supprime puis recrée. Sur une base qui
-- contient déjà des données, il les efface. C'est voulu tant qu'on est en
-- phase 1 ; à retirer le jour où la base fait foi.
-- ============================================================================

drop table if exists menu_lignes cascade;
drop table if exists menus       cascade;
drop table if exists produits    cascade;
drop table if exists marches     cascade;
drop table if exists avis        cascade;
drop table if exists reglages    cascade;
drop type  if exists famille_produit cascade;
drop type  if exists categorie_plat  cascade;
drop type  if exists type_marche     cascade;
drop type  if exists bloc_menu       cascade;


-- ---------------------------------------------------------------------------
-- Horodatage automatique
-- ---------------------------------------------------------------------------
-- « modifie_le timestamptz default now() » ne se met à jour qu'à l'insertion :
-- une modification ultérieure laisserait la date d'origine. Sans ce déclencheur
-- la colonne mentirait, ce qui est pire que de ne pas l'avoir.

create or replace function marquer_modification()
returns trigger
language plpgsql
as $$
begin
  new.modifie_le = now();
  return new;
end;
$$;


-- ---------------------------------------------------------------------------
-- Ce que l'on vend, à la part
-- ---------------------------------------------------------------------------
-- ÉCART 1 — « buffet » retiré de l'énumération des familles.
-- Dans data/carte.json, le buffet n'est pas une famille de produits : c'est un
-- bloc rédactionnel (un titre, un paragraphe, six libellés sans prix ni photo).
-- L'y ranger obligerait à inventer un slug et un prix pour « Samoussas », et
-- ferait disparaître le titre et le texte. Il va dans reglages.mentions, avec
-- les autres textes de la carte.

create type famille_produit as enum ('plat', 'entree', 'boisson', 'supplement');
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
  modifie_le   timestamptz not null default now(),

  -- ÉCART 2 — la règle « categorie seulement pour les plats » était en
  -- commentaire dans le cahier des charges. Un commentaire n'empêche rien : le
  -- jour où le backoffice enverra une catégorie sur une boisson, la base
  -- l'acceptera et les filtres de la carte se mettront à mentir. On l'écrit.
  constraint categorie_reservee_aux_plats
    check ((famille = 'plat') = (categorie is not null)),

  constraint prix_positif check (prix is null or prix >= 0)
);

create index on produits (famille, ordre);

create trigger produits_modifie
  before update on produits
  for each row execute function marquer_modification();


-- ---------------------------------------------------------------------------
-- Les menus, et leur composition
-- ---------------------------------------------------------------------------

create table menus (
  id                uuid primary key default gen_random_uuid(),
  slug              text not null unique,
  nom               text not null,
  resume            text not null default '',
  prix              numeric(6,2) not null,
  prix_max          numeric(6,2),          -- null si prix unique
  supplement_motif  text,                  -- « avec un plat poisson… »
  ordre             integer not null default 0,
  actif             boolean not null default true,
  modifie_le        timestamptz not null default now(),

  -- Un prix haut inférieur au prix bas afficherait « 22 à 18 € » sur le site.
  constraint fourchette_coherente check (prix_max is null or prix_max >= prix)
);

create trigger menus_modifie
  before update on menus
  for each row execute function marquer_modification();

create type bloc_menu as enum ('entree', 'plat', 'dessert', 'inclus');

-- Une ligne par élément : c'est la relation un-à-plusieurs du projet.
-- « on delete cascade » : supprimer un menu emporte ses lignes. Sans cela, la
-- suppression échouerait, et des lignes orphelines resteraient en base.
create table menu_lignes (
  id       uuid primary key default gen_random_uuid(),
  menu_id  uuid not null references menus(id) on delete cascade,
  bloc     bloc_menu not null,
  libelle  text not null,
  ordre    integer not null default 0
);

create index on menu_lignes (menu_id, bloc, ordre);


-- ---------------------------------------------------------------------------
-- Les marchés
-- ---------------------------------------------------------------------------

create type type_marche as enum ('matin', 'nocturne');

create table marches (
  id         uuid primary key default gen_random_uuid(),
  lieu       text not null,
  jour       text not null,        -- « mardi » … ou « 2026-12-14 » pour une date unique
  type       type_marche not null default 'matin',
  horaire    text not null default '',

  -- ÉCART 3 — « precision » est un mot-clé du SQL standard (DOUBLE PRECISION).
  -- L'utiliser comme nom de colonne oblige à l'entourer de guillemets dans
  -- chaque requête, et un oubli donne une erreur de syntaxe obscure.
  -- Renommé « details » ; l'exportateur le réécrira en « precision » dans le
  -- JSON, où la clé ne gêne personne.
  details    text not null default '',

  jusquau    date,                 -- null = pas de fin de saison
  ordre      integer not null default 0,
  actif      boolean not null default true,

  -- site.js et generer-html.py n'acceptent que ces deux formes. Une faute de
  -- frappe (« Mardi », « mardis ») ferait disparaître le marché de la page
  -- sans le moindre message d'erreur : la panne la plus désagréable qui soit.
  constraint jour_valide check (
    jour in ('lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche')
    or jour ~ '^\d{4}-\d{2}-\d{2}$'
  )
);

create index on marches (ordre);


-- ---------------------------------------------------------------------------
-- Les avis
-- ---------------------------------------------------------------------------
-- ÉCART 4 — « date_avis » retiré. data/avis.json n'a pas ce champ : la date est
-- déjà dans « contexte » (« Avis Facebook, avril 2026 »). Deux colonnes pour la
-- même information finissent toujours par se contredire.

create table avis (
  id        uuid primary key default gen_random_uuid(),
  auteur    text not null,        -- prénom + initiale, jamais le nom complet
  note      smallint not null check (note between 1 and 5),
  contexte  text not null default '',   -- « Mariage à Coutras, juin 2026 »
  texte     text not null,
  publie    boolean not null default false,
  ordre     integer not null default 0
);


-- ---------------------------------------------------------------------------
-- Les réglages : une seule ligne, verrouillée
-- ---------------------------------------------------------------------------
-- « id boolean primary key default true check (id) » : la clé primaire interdit
-- deux lignes ayant la même valeur, et la contrainte interdit toute valeur
-- autre que « true ». Il ne reste donc qu'une seule ligne possible.

create table reglages (
  id                      boolean primary key default true check (id),

  -- Ce que Karine modifie réellement (onglet « Réglages »).
  telephone               text not null,
  telephone_lien          text not null,
  email                   text not null,
  ville_affichee          text not null,
  minimum_parts           integer not null default 10,
  frais_livraison_proche  numeric(6,2) not null default 5,
  frais_livraison_loin    numeric(6,2) not null default 10,
  rayon_livraison_km      integer not null default 50,
  facebook                text not null default '',
  instagram               text not null default '',
  google_business_profile text not null default '',
  avis_google_note        text not null default '',
  avis_google_nombre      text not null default '',
  avis_facebook_taux      text not null default '',
  avis_facebook_nombre    text not null default '',
  abonnes_facebook        text not null default '',

  -- ÉCART 5 — un gabarit unique, de type « json » et non « jsonb ».
  --
  -- Le cahier des charges proposait de loger « le reste » dans un jsonb. Deux
  -- corrections, l'une et l'autre vérifiables en relançant
  -- outils/verifier-modele.py :
  --
  -- 1. jsonb normalise. Il réordonne les clés (par longueur, puis par octet)
  --    et supprime les doublons. config.json compte une quarantaine de clés
  --    rangées dans un ordre voulu, entrecoupées de clés « _lisezmoi » qui
  --    tiennent lieu de commentaires. Passé par jsonb, le fichier reviendrait
  --    mélangé. « json » conserve le texte tel quel ; on perd l'indexation,
  --    dont on n'a aucun usage sur une ligne unique.
  --
  -- 2. Stocker « le reste » ne suffit pas : il faut aussi savoir OÙ le
  --    remettre. carte.json intercale « _supplements » entre le buffet et les
  --    suppléments ; config.json alterne commentaires et valeurs. Une base ne
  --    connaît pas l'ordre des clés d'un fichier.
  --
  -- Le gabarit résout les deux : il contient les quatre fichiers JSON tels
  -- quels, où les seules parties pilotées par la base sont remplacées par un
  -- repère — « @produits:plat », « @menus », « @reglage:telephone ». À la
  -- publication, outils/modele.py parcourt le gabarit et remplace les repères
  -- par les données fraîches. L'ordre et les commentaires sont conservés sans
  -- qu'aucun script ait à les connaître.
  gabarits                json not null default '{}',

  modifie_le              timestamptz not null default now()
);

create trigger reglages_modifie
  before update on reglages
  for each row execute function marquer_modification();


-- ============================================================================
-- Sécurité (CDC § 5)
-- ============================================================================
-- Le site public ne lit jamais cette base : il lit du HTML statique. Personne
-- d'autre que Karine et Romu n'a donc besoin d'y accéder. D'où une règle unique
-- et stricte : tout est fermé, sauf aux personnes connectées.
--
-- Piège : activer RLS sans créer de politique rend la table muette. Aucune
-- erreur, juste zéro ligne renvoyée. Les deux vont toujours ensemble.

alter table produits    enable row level security;
alter table menus       enable row level security;
alter table menu_lignes enable row level security;
alter table marches     enable row level security;
alter table avis        enable row level security;
alter table reglages    enable row level security;

create policy "connectes: tout" on produits
  for all to authenticated using (true) with check (true);

create policy "connectes: tout" on menus
  for all to authenticated using (true) with check (true);

create policy "connectes: tout" on menu_lignes
  for all to authenticated using (true) with check (true);

create policy "connectes: tout" on marches
  for all to authenticated using (true) with check (true);

create policy "connectes: tout" on avis
  for all to authenticated using (true) with check (true);

create policy "connectes: tout" on reglages
  for all to authenticated using (true) with check (true);


-- ============================================================================
-- Vérification
-- ============================================================================
-- À exécuter après coup. Les six tables doivent apparaître avec rls_active = t
-- et politiques = 1. Une table à 0 politique est une table muette.

--   select c.relname                as table,
--          c.relrowsecurity         as rls_active,
--          count(p.polname)         as politiques
--     from pg_class c
--     left join pg_policy p on p.polrelid = c.oid
--    where c.relnamespace = 'public'::regnamespace
--      and c.relkind = 'r'
--    group by 1, 2
--    order by 1;
