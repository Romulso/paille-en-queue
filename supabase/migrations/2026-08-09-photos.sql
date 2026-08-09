-- ============================================================================
-- Boite de transit pour les photos de plats
-- ============================================================================
--
-- Fichier en pur ASCII, comme les autres.
-- A executer dans l'editeur SQL de Supabase.
--
--
-- POURQUOI UNE BOITE DE TRANSIT, ET NON UN HEBERGEMENT
-- ----------------------------------------------------
-- Le cahier des charges l'interdit formellement (section  2) : le site public ne doit
-- jamais dependre de Supabase. Faire pointer les <img> du site vers Storage
-- serait commode, mais le jour ou le projet gratuit se met en pause, toutes
-- les photos disparaitraient du site.
--
-- Ce bucket ne sert donc qu'au transport :
--   1. Karine depose la photo depuis le backoffice ;
--   2. la publication la telecharge, la met au format des autres photos,
--      fabrique l'AVIF et le WebP, et commit le tout dans images/ ;
--   3. la publication vide le bucket.
--
-- Le site continue de servir ses propres fichiers. Storage est vide la plupart
-- du temps, ce qui est le signe que tout fonctionne.
--
--
-- Le bucket est PRIVE. Le site n'a pas besoin d'y lire : seuls le backoffice
-- (compte de Karine) et la publication (cle secrete) y accedent.
-- ============================================================================


insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('photos-plats', 'photos-plats', false, 15728640,
        array['image/jpeg', 'image/png', 'image/webp', 'image/heic'])
on conflict (id) do update
  set public = false,
      file_size_limit = excluded.file_size_limit,
      allowed_mime_types = excluded.allowed_mime_types;


-- ---------------------------------------------------------------------------
-- Securite
-- ---------------------------------------------------------------------------
-- Meme regle que partout ailleurs : les comptes connus, et personne d'autre.
-- La cle secrete utilisee par la publication contourne ces politiques, ce qui
-- lui permet de vider le bucket.

drop policy if exists "comptes autorises: deposer une photo" on storage.objects;
drop policy if exists "comptes autorises: lire les photos"   on storage.objects;
drop policy if exists "comptes autorises: remplacer"         on storage.objects;
drop policy if exists "comptes autorises: supprimer"         on storage.objects;

create policy "comptes autorises: deposer une photo" on storage.objects
  for insert to authenticated
  with check (bucket_id = 'photos-plats' and public.est_autorise());

create policy "comptes autorises: lire les photos" on storage.objects
  for select to authenticated
  using (bucket_id = 'photos-plats' and public.est_autorise());

create policy "comptes autorises: remplacer" on storage.objects
  for update to authenticated
  using (bucket_id = 'photos-plats' and public.est_autorise())
  with check (bucket_id = 'photos-plats' and public.est_autorise());

create policy "comptes autorises: supprimer" on storage.objects
  for delete to authenticated
  using (bucket_id = 'photos-plats' and public.est_autorise());


-- ---------------------------------------------------------------------------
-- Controle
-- ---------------------------------------------------------------------------
--   select id, public, file_size_limit from storage.buckets where id = 'photos-plats';
--   select polname from pg_policy where polrelid = 'storage.objects'::regclass;
