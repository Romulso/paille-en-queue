-- ============================================================================
-- Mesure d'audience du formulaire de devis
-- ============================================================================
--
-- Fichier en pur ASCII, comme les autres : le trajet presse-papiers puis
-- navigateur peut reinterpreter l'UTF-8 en chemin.
--
--
-- POURQUOI CETTE TABLE EXISTE
-- ---------------------------
-- Le 26 septembre 2026, une cliente a signale ne pas pouvoir valider sa
-- demande de devis. Le defaut datait du premier jour du site, le 27 juillet :
-- soixante et un jours pendant lesquels aucune demande n'a abouti, sans que
-- personne puisse s'en apercevoir. Le site n'avait aucune mesure d'audience.
--
-- Quatre compteurs suffisent a ce que cela ne se reproduise pas :
--
--   devis_ouvert     la page du formulaire a ete ouverte
--   devis_commence   le visiteur a commence a remplir
--   devis_bloque     la validation a refuse l'envoi (detail = champ fautif)
--   devis_envoye     la demande est partie
--
-- Un ecart entre "commence" et "envoye" se voit en une semaine. Et
-- "devis_bloque" nomme directement le champ qui coince : le defaut de
-- septembre aurait saute aux yeux des le premier jour.
--
--
-- CE QUI N'EST PAS ENREGISTRE
-- ---------------------------
-- Aucune donnee personnelle. Pas d'adresse IP, pas de cookie, pas
-- d'identifiant de visiteur, pas de page precedente, pas de navigateur. Une
-- ligne par jour et par evenement, avec un simple compteur. Il est donc
-- impossible de reconstituer le parcours d'une personne, et la mesure ne
-- releve ni de l'article 82 de la loi Informatique et Libertes, ni du
-- consentement prealable : il n'y a pas de bandeau a afficher.
--
-- En contrepartie les chiffres sont indicatifs et non certifies : rien
-- n'empeche quelqu'un d'appeler la fonction en boucle pour les gonfler. Ils
-- servent a reperer une rupture, pas a etablir une facture.
--
--
-- POURQUOI UNE FONCTION PLUTOT QU'UNE TABLE OUVERTE
-- -------------------------------------------------
-- La cle publique du site est lisible par tout le monde : elle est dans le
-- depot. Si la table acceptait l'insertion directe, n'importe qui pourrait y
-- ecrire n'importe quoi, y compris du texte libre. Le visiteur n'a donc aucun
-- droit sur la table : il ne peut qu'appeler compter(), qui refuse en silence
-- tout evenement hors de la liste et tronque le detail a 60 caracteres.
-- ============================================================================

create table if not exists mesures (
  jour       date    not null default current_date,
  evenement  text    not null,
  detail     text    not null default '',
  compteur   integer not null default 0,
  primary key (jour, evenement, detail)
);

comment on table mesures is
  U&'Compteurs d\0027audience, agr\00e9g\00e9s par jour. Aucune donn\00e9e personnelle.';

-- Les releves se lisent du plus recent au plus ancien.
create index if not exists mesures_jour_desc on mesures (jour desc);

alter table mesures enable row level security;

-- Le visiteur n'a aucun droit direct : tout passe par la fonction ci-dessous.
-- Seul le backoffice, authentifie, peut relire les compteurs.
drop policy if exists "comptes autorises: lire les mesures" on mesures;
create policy "comptes autorises: lire les mesures" on mesures
  for select to authenticated using (public.est_autorise());

-- ----------------------------------------------------------------------------
-- compter() : le seul chemin d'ecriture ouvert au site public.
--
-- security definer, donc elle s'execute avec les droits de son proprietaire et
-- traverse la politique ci-dessus. C'est voulu : c'est elle qui tient lieu de
-- controle, en n'acceptant que les quatre evenements connus.
-- ----------------------------------------------------------------------------
create or replace function public.compter(p_evenement text, p_detail text default '')
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  if p_evenement not in ('devis_ouvert', 'devis_commence',
                         'devis_bloque', 'devis_envoye') then
    return;                     -- on ignore en silence ce qu'on ne connait pas
  end if;

  insert into mesures (jour, evenement, detail, compteur)
  values (current_date, p_evenement, left(coalesce(p_detail, ''), 60), 1)
  on conflict (jour, evenement, detail)
  do update set compteur = mesures.compteur + 1;
end;
$$;

comment on function public.compter(text, text) is
  U&'Incr\00e9mente un compteur d\0027audience. Seule \00e9criture ouverte au site public.';

revoke all on function public.compter(text, text) from public;
grant execute on function public.compter(text, text) to anon, authenticated;
