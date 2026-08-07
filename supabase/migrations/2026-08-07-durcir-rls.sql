-- ============================================================================
-- Restreindre l'acces aux seuls comptes connus
-- ============================================================================
--
-- Applique le 07/08/2026 sur la base existante. Le contenu est repris dans
-- supabase/schema.sql, qui reste la reference pour une base neuve.
--
-- Fichier en pur ASCII, comme donnees-initiales.sql : le trajet
-- presse-papiers puis navigateur peut reinterpreter l'UTF-8 en chemin. Les
-- rares accents utiles sont ecrits en U&'...\00e9...' et decodes par
-- PostgreSQL lui-meme.
--
-- Pourquoi
-- --------
-- La politique d'origine ouvrait les six tables a tout compte connecte.
-- C'etait suffisant tant que personne ne peut creer de compte -- mais
-- l'inscription est justement restee ouverte pendant les premieres heures du
-- projet, sans que rien ne le signale. La cle publishable figure dans un
-- depot public : il suffisait alors de s'inscrire pour obtenir la lecture ET
-- l'ecriture sur la carte et les prix.
--
-- L'inscription est desormais fermee. Cette migration ajoute la seconde
-- serrure : meme rouverte par megarde, elle ne donnerait plus rien.
--
-- Ajouter une personne
-- --------------------
-- Une seule ligne a modifier, dans est_autorise() ci-dessous. Attention : un
-- compte absent de cette liste ne verra aucune erreur, seulement des tableaux
-- vides. C'est le prix de cette protection.
-- ============================================================================


-- La fonction est "stable" : son resultat ne change pas au sein d'une meme
-- requete, ce qui permet a PostgreSQL de ne l'evaluer qu'une fois au lieu
-- d'une fois par ligne.
create or replace function public.est_autorise()
returns boolean
language sql
stable
as $$
  select coalesce(auth.jwt() ->> 'email', '') in (
    'lepailleenqueue33@gmail.com'
  );
$$;

comment on function public.est_autorise() is
  U&'Comptes autoris\00e9s sur le backoffice. Ajouter une adresse ici suffit.';


drop policy if exists "connectes: tout" on produits;
drop policy if exists "connectes: tout" on menus;
drop policy if exists "connectes: tout" on menu_lignes;
drop policy if exists "connectes: tout" on marches;
drop policy if exists "connectes: tout" on avis;
drop policy if exists "connectes: tout" on reglages;

create policy "comptes autorises: tout" on produits
  for all to authenticated using (public.est_autorise()) with check (public.est_autorise());

create policy "comptes autorises: tout" on menus
  for all to authenticated using (public.est_autorise()) with check (public.est_autorise());

create policy "comptes autorises: tout" on menu_lignes
  for all to authenticated using (public.est_autorise()) with check (public.est_autorise());

create policy "comptes autorises: tout" on marches
  for all to authenticated using (public.est_autorise()) with check (public.est_autorise());

create policy "comptes autorises: tout" on avis
  for all to authenticated using (public.est_autorise()) with check (public.est_autorise());

create policy "comptes autorises: tout" on reglages
  for all to authenticated using (public.est_autorise()) with check (public.est_autorise());


-- Controle : six tables, RLS actif, une politique chacune.
select c.relname as "table", c.relrowsecurity as rls_active, count(p.polname) as politiques
  from pg_class c
  left join pg_policy p on p.polrelid = c.oid
 where c.relnamespace = 'public'::regnamespace and c.relkind = 'r'
 group by 1, 2 order by 1;
