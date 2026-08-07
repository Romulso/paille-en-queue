-- ============================================================================
-- Carnet de commandes : les demandes de devis
-- ============================================================================
--
-- Fichier en pur ASCII, comme les autres : le trajet presse-papiers puis
-- navigateur peut reinterpreter l'UTF-8 en chemin.
--
-- A executer dans l'editeur SQL de Supabase, apres les migrations
-- precedentes. Ne touche a aucune table existante.
--
--
-- ATTENTION, LA REGLE A NE JAMAIS ENFREINDRE
-- ------------------------------------------
-- Cette table contient des donnees personnelles de clients : noms, adresses,
-- telephones. Le depot GitHub est PUBLIC, et la chaine de publication y ecrit
-- data/*.json a chaque passage.
--
-- La table "demandes" ne doit donc JAMAIS figurer dans la liste TABLES de
-- outils/exporter-supabase.py, ni dans aucun gabarit. Elle vit dans la base
-- et n'en sort que par le backoffice, derriere authentification.
--
--
-- Pourquoi le site public peut ecrire ici
-- ---------------------------------------
-- Un visiteur n'est pas connecte. Pour que sa demande arrive en base, la
-- politique "anon" l'autorise a INSERER, et uniquement cela : pas de
-- lecture, pas de modification, pas de suppression. Personne ne peut donc
-- lire les demandes des autres avec la cle publique.
--
-- L'e-mail reste le canal principal : le formulaire part d'abord chez
-- Formspree, et l'ecriture en base vient apres, sans bloquer. Si Supabase est
-- indisponible, la demande arrive quand meme dans la boite de Karine.
-- ============================================================================


drop table if exists demandes cascade;
drop type  if exists etat_demande cascade;

create type etat_demande as enum (
  'nouveau', 'devis_envoye', 'signe', 'realise', 'sans_suite'
);

create table demandes (
  id           uuid primary key default gen_random_uuid(),
  recu_le      timestamptz not null default now(),

  -- Qui demande
  nom          text not null check (length(nom) between 1 and 120),
  email        text check (email is null or length(email) <= 160),
  telephone    text check (telephone is null or length(telephone) <= 40),
  structure    text check (structure is null or length(structure) <= 160),
  rappel       boolean not null default false,

  -- L'evenement
  type_evenement text check (type_evenement is null or length(type_evenement) <= 120),
  date_evenement date,
  heure_service  text check (heure_service is null or length(heure_service) <= 20),
  convives       integer check (convives is null or convives between 1 and 5000),
  commune        text check (commune is null or length(commune) <= 120),
  type_lieu      text check (type_lieu is null or length(type_lieu) <= 120),

  -- Ce qui est souhaite
  style_cuisine    text check (style_cuisine is null or length(style_cuisine) <= 120),
  formule          text check (formule is null or length(formule) <= 160),
  budget           text check (budget is null or length(budget) <= 60),
  plats            text[] not null default '{}',
  entrees_boissons text[] not null default '{}',
  supplements      text[] not null default '{}',
  precisions       text check (precisions is null or length(precisions) <= 4000),

  -- Le suivi, rempli par Karine dans le backoffice
  etat  etat_demande not null default 'nouveau',
  suivi text not null default '',

  -- Piege a robots. Le formulaire du site laisse ce champ vide et cache ;
  -- un automate le remplit et se fait refuser par la contrainte, sans qu'on
  -- ait besoin d'ecrire la moindre ligne de code cote serveur.
  piege text not null default '' check (piege = '')
);

-- Les demandes se consultent de la plus recente a la plus ancienne.
create index on demandes (recu_le desc);

comment on table demandes is
  U&'Demandes de devis. Donn\00e9es personnelles : ne jamais exporter vers le d\00e9p\00f4t public.';


-- ---------------------------------------------------------------------------
-- Securite
-- ---------------------------------------------------------------------------

alter table demandes enable row level security;

-- Le visiteur depose sa demande, et rien d'autre. Pas de politique de
-- lecture pour "anon" : la cle publique ne permet pas de relire ce qui a
-- ete envoye, ni par soi-meme ni par les autres.
--
-- Le "with check" verrouille en plus les deux colonnes de suivi : un
-- visiteur ne peut pas se declarer "signe", ni preremplir les notes.
create policy "visiteurs: deposer une demande" on demandes
  for insert to anon
  with check (etat = 'nouveau' and suivi = '' and piege = '');

-- Karine et Romu, via le backoffice.
create policy "comptes autorises: tout" on demandes
  for all to authenticated
  using (public.est_autorise()) with check (public.est_autorise());


-- ---------------------------------------------------------------------------
-- Controle
-- ---------------------------------------------------------------------------
-- Attendu : rls_active = t, et 2 politiques.
--
--   select c.relname, c.relrowsecurity, count(p.polname)
--     from pg_class c left join pg_policy p on p.polrelid = c.oid
--    where c.relname = 'demandes' group by 1, 2;
