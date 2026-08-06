-- ==========================================================================
-- Le Paille en Queue — données initiales
-- ==========================================================================
--
-- Fichier ENGENDRÉ par outils/generer-seed-supabase.py.
-- Ne pas le modifier à la main : modifier data/*.json et relancer.
--
-- À exécuter dans l'éditeur SQL de Supabase, après schema.sql.
-- Ré-exécutable : les tables sont vidées avant remplissage.
-- ==========================================================================

-- « cascade » vide aussi menu_lignes, qui référence menus.
truncate menu_lignes, menus, produits, marches, avis, reglages cascade;

-- --------------------------------------------------------------------------
-- Produits (22)
-- --------------------------------------------------------------------------
insert into produits (famille, slug, nom, description, prix, unite, categorie, vedette, ordre, actif) values
  ('plat', 'rougail-saucisses', 'Rougail saucisses', 'Le plat du dimanche à La Réunion. Saucisses fumées mijotées longuement dans une sauce tomate parfumée au gingembre, au curcuma, à l''oignon et au thym.', 10, null, 'porc', true, 0, true),
  ('plat', 'rougail-morue', 'Rougail morue', 'Morue dessalée et effeuillée, tomates fraîches, oignons et gingembre. Un classique créole franc et iodé.', 12, null, 'mer', false, 1, true),
  ('plat', 'cari-poulet', 'Cari poulet', 'Le cari de base de la cuisine réunionnaise : poulet doré puis mijoté avec oignon, ail, gingembre, curcuma et tomate.', 10, null, 'volaille', false, 2, true),
  ('plat', 'poulet-massale', 'Poulet massalé', 'Poulet au massalé, le mélange d''épices grillées de l''océan Indien : coriandre, cumin, girofle, cannelle. Chaleureux et très parfumé.', 10, null, 'volaille', true, 3, true),
  ('plat', 'poulet-coco', 'Poulet coco', 'Poulet fondant au lait de coco, adouci par les épices. Le plat qui met tout le monde d''accord, y compris les enfants.', 10, null, 'volaille', false, 4, true),
  ('plat', 'poulet-ananas', 'Poulet ananas', 'Sucré-salé créole : poulet mijoté et ananas caramélisé. Surprenant et redoutablement efficace en buffet.', 10, null, 'volaille', false, 5, true),
  ('plat', 'poulet-colombo', 'Poulet colombo', 'Poulet au colombo, épice des Antilles adoptée dans tout l''océan Indien. Rond, doux, légèrement acidulé.', 10, null, 'volaille', false, 6, true),
  ('plat', 'curry-dinde', 'Curry de dinde', 'Dinde mijotée au curry, une viande légère qui passe très bien en repas d''entreprise et en grande tablée.', 10, null, 'volaille', false, 7, true),
  ('plat', 'porc-colombo', 'Porc colombo', 'Échine de porc mijotée au colombo jusqu''à s''effilocher, dans une sauce généreuse.', 10, null, 'porc', false, 8, true),
  ('plat', 'porc-ananas', 'Porc ananas', 'Porc caramélisé à l''ananas, l''accord sucré-salé qui fait la signature de la cuisine des îles.', 10, null, 'porc', false, 9, true),
  ('plat', 'lentilles-boucane', 'Lentilles boucané', 'Lentilles fondantes et poitrine de porc fumée au bois : le boucané. Le plat réunionnais le plus réconfortant qui soit.', 10, null, 'porc', false, 10, true),
  ('plat', 'boeuf-massale', 'Bœuf massalé', 'Bœuf longuement mijoté au massalé, jusqu''à ce que la viande se défasse à la cuillère.', 10, null, 'boeuf-agneau', true, 11, true),
  ('plat', 'cari-agneau', 'Cari d''agneau', 'Agneau en cari, relevé de gingembre frais et de curcuma. Une valeur sûre pour les repas de fête.', 12, null, 'boeuf-agneau', false, 12, true),
  ('plat', 'cari-poisson-crevettes', 'Cari poisson ou crevettes', 'Cari de poisson (espadon selon arrivage) ou de crevettes, monté sur un massalé léger pour ne pas couvrir le produit.', 12, null, 'mer', true, 13, true),
  ('plat', 'crevettes-coco', 'Crevettes coco', 'Crevettes nacrées dans un lait de coco parfumé au combava et au gingembre. Le plat le plus demandé sur les buffets.', 12, null, 'mer', true, 14, true),
  ('entree', 'samoussas', 'Samoussas', 'Pliés et frits à la commande. Six garnitures : thon, porc, poulet, poisson, fromage et végan.', 1, 'la pièce', null, true, 0, true),
  ('entree', 'accras-morue', 'Accras de morue', 'Beignets de morue moelleux au cœur, croustillants dehors. Ils ne survivent jamais longtemps à l''apéritif.', 7, 'les 16', null, true, 1, true),
  ('entree', 'bouchons', 'Bouchons', 'Les petites bouchées vapeur réunionnaises, héritage chinois de l''île. Servies avec leur sauce.', 5, 'les 6', null, true, 2, true),
  ('boisson', 'punch-planteur', 'Punch planteur', 'Notre planteur maison, préparé la veille pour que les fruits aient le temps de parfumer le rhum.', 12, 'le litre', null, false, 0, true),
  ('supplement', 'pain', 'Pain', 'Pain frais du jour, compté par convive.', 1, 'par personne', null, false, 0, true),
  ('supplement', 'vaisselle', 'Vaisselle', 'Assiettes et couverts en carton et en bois. Solide, propre et compostable.', 0.4, 'par personne', null, false, 1, true),
  ('supplement', 'service', 'Service à table', 'Une ou plusieurs personnes pour dresser, servir et débarrasser. Chiffré selon la durée et le nombre de convives.', null, 'sur devis', null, false, 2, true);

-- --------------------------------------------------------------------------
-- Menus (3) et leur composition (28 lignes)
-- --------------------------------------------------------------------------
insert into menus (slug, nom, resume, prix, prix_max, supplement_motif, ordre, actif) values
  ('menu-creole', 'Menu Créole', 'L''essentiel de la table réunionnaise, en trois services.', 18, null, null, 0, true),
  ('menu-lagon', 'Menu Lagon', 'Une entrée à l''assiette et des plats plus généreux : le menu des grandes occasions.', 24, 26, 'avec un plat poisson, crevettes ou morue', 1, true),
  ('menu-volcan', 'Menu Volcan', 'Notre menu le plus abouti, construit autour des produits les plus nobles de la carte.', 28, 30, 'avec un plat poisson, crevettes ou morue', 2, true);

insert into menu_lignes (menu_id, bloc, libelle, ordre) values
  ((select id from menus where slug = 'menu-creole'), 'entree', 'Salade d''accras de morue', 0),
  ((select id from menus where slug = 'menu-creole'), 'entree', '2 samoussas au choix', 1),
  ((select id from menus where slug = 'menu-creole'), 'plat', 'Cari poisson ou crevettes', 0),
  ((select id from menus where slug = 'menu-creole'), 'plat', 'Poulet coco, ananas, massalé ou colombo', 1),
  ((select id from menus where slug = 'menu-creole'), 'plat', 'Porc, dinde ou rougail saucisses', 2),
  ((select id from menus where slug = 'menu-creole'), 'dessert', 'Salade de fruits de saison', 0),
  ((select id from menus where slug = 'menu-creole'), 'inclus', 'Riz et sauce piquante', 0),
  ((select id from menus where slug = 'menu-lagon'), 'entree', 'Assiette de brochettes de crevettes à la plancha', 0),
  ((select id from menus where slug = 'menu-lagon'), 'entree', '2 samoussas au choix', 1),
  ((select id from menus where slug = 'menu-lagon'), 'entree', 'Accras de morue', 2),
  ((select id from menus where slug = 'menu-lagon'), 'plat', 'Poulet colombo', 0),
  ((select id from menus where slug = 'menu-lagon'), 'plat', 'Curry de dinde', 1),
  ((select id from menus where slug = 'menu-lagon'), 'plat', 'Bœuf massalé', 2),
  ((select id from menus where slug = 'menu-lagon'), 'plat', 'Crevettes coco', 3),
  ((select id from menus where slug = 'menu-lagon'), 'plat', 'Cari d''agneau', 4),
  ((select id from menus where slug = 'menu-lagon'), 'dessert', 'Salade de fruits exotiques selon la saison', 0),
  ((select id from menus where slug = 'menu-lagon'), 'dessert', 'Part de gâteau', 1),
  ((select id from menus where slug = 'menu-lagon'), 'inclus', 'Riz et sauce piquante', 0),
  ((select id from menus where slug = 'menu-volcan'), 'entree', 'Crevettes coco', 0),
  ((select id from menus where slug = 'menu-volcan'), 'entree', '2 samoussas au choix', 1),
  ((select id from menus where slug = 'menu-volcan'), 'entree', 'Accras de morue', 2),
  ((select id from menus where slug = 'menu-volcan'), 'plat', 'Bœuf massalé', 0),
  ((select id from menus where slug = 'menu-volcan'), 'plat', 'Cari d''agneau', 1),
  ((select id from menus where slug = 'menu-volcan'), 'plat', 'Cari crevettes ou poisson (espadon)', 2),
  ((select id from menus where slug = 'menu-volcan'), 'plat', 'Curry de dinde aux cèpes', 3),
  ((select id from menus where slug = 'menu-volcan'), 'dessert', 'Salade de fruits de saison', 0),
  ((select id from menus where slug = 'menu-volcan'), 'dessert', 'Part de gâteau', 1),
  ((select id from menus where slug = 'menu-volcan'), 'inclus', 'Riz et sauce piquante', 0);

-- --------------------------------------------------------------------------
-- Marchés (5)
-- --------------------------------------------------------------------------
insert into marches (lieu, jour, type, horaire, details, jusquau, ordre, actif) values
  ('Le Pizou', 'mardi', 'nocturne', 'À partir de 19 h', 'Marché nocturne d''été', '2026-08-31', 0, true),
  ('Saint-Laurent-des-Hommes', 'mercredi', 'nocturne', 'À partir de 19 h', 'Marché nocturne d''été', '2026-08-17', 1, true),
  ('Communes variables', 'vendredi', 'nocturne', 'À partir de 19 h', 'La commune change chaque semaine : appelez-nous ou consultez notre page Facebook.', null, 2, true),
  ('Communes variables', 'samedi', 'nocturne', 'À partir de 19 h', 'La commune change chaque semaine : appelez-nous ou consultez notre page Facebook.', null, 3, true),
  ('Saint-Seurin-sur-l''Isle', 'dimanche', 'matin', '', '', null, 4, true);

-- --------------------------------------------------------------------------
-- Avis (1)
-- --------------------------------------------------------------------------
insert into avis (auteur, note, contexte, texte, publie, ordre) values
  ('Angèle M.', 5, 'Avis Facebook, avril 2026', 'Ayant des racines créoles, c''est de loin le seul endroit où on se croit à La Réunion quand on mange leurs plats. Je recommande à 200 %, et en plus la sympathie pour aller avec. Bref : au top.', true, 0);

-- --------------------------------------------------------------------------
-- Réglages — ligne unique, gabarits compris
-- --------------------------------------------------------------------------
insert into reglages (telephone, telephone_lien, email, ville_affichee, minimum_parts, frais_livraison_proche, frais_livraison_loin, rayon_livraison_km, facebook, instagram, google_business_profile, avis_google_note, avis_google_nombre, avis_facebook_taux, avis_facebook_nombre, abonnes_facebook, gabarits) values
  ('06 27 35 23 28', '+33627352328', 'contact@lepaille-en-queue.fr', 'Montpeyroux (24)', 10, 5, 10, 50, 'https://www.facebook.com/share/1FLfRCbbv9/?mibextid=wwXIfr', '', 'https://www.google.com/maps?cid=13538170108796715746', '5,0', '4', '100 %', '29', '2 900', '{
  "carte": {
    "_lisezmoi": "La carte complète. Modifiable depuis admin.html (onglet Carte). Les prix sont en euros, par part. Le champ « image » pointe vers images/<nom-du-fichier> : tant que le fichier n''existe pas, le site affiche un joli aplat coloré à la place.",
    "mentionPart": "Tous les plats sont servis avec le riz et la sauce piquante.",
    "mentionMinimum": "Commande à partir de 10 parts.",
    "mentionNonCompris": "Le service, la vaisselle et le pain ne sont jamais compris dans nos prix. Pain 1 € et vaisselle 0,40 € par personne, service sur devis.",
    "mentionLivraison": "Nous nous déplaçons jusqu''à 50 km autour de Montpeyroux : livraison 5 € jusqu''à 10 km, 10 € au-delà. Plus loin, sur devis.",
    "mentionDelai": "Commande à passer 4 à 5 jours à l''avance.",
    "plats": "@produits:plat",
    "entrees": "@produits:entree",
    "buffet": {
      "titre": "En buffet",
      "texte": "Pour un cocktail, un vin d''honneur ou une inauguration, nous composons un buffet créole à partager.",
      "elements": [
        "Bouchons",
        "Samoussas",
        "Accras de morue",
        "Boudins créoles",
        "Brochettes tomate-fromage",
        "Brochettes de crevettes à la plancha"
      ]
    },
    "_supplements": "Prestations jamais comprises dans les prix, facturées en plus si le client les demande. Un prix à null s''affiche « sur devis ».",
    "supplements": "@produits:supplement",
    "boissons": "@produits:boisson",
    "menus": "@menus"
  },
  "marches": {
    "_lisezmoi": "Les marchés où Karine est présente. Modifiable depuis admin.html (onglet Marchés). « jour » : lundi…dimanche pour un marché hebdomadaire, ou une date au format AAAA-MM-JJ pour une date unique. « type » : matin ou nocturne. « jusquau » (facultatif, AAAA-MM-JJ) borne un marché de saison : passée cette date, il disparaît tout seul de la page. Tant que la liste est vide, la page affiche une invitation à téléphoner.",
    "marches": "@marches"
  },
  "avis": {
    "_lisezmoi": "Témoignages de clients. Modifiable depuis admin.html (onglet Avis). N''y mettre que de VRAIS avis, avec l''accord de la personne : un faux témoignage est interdit par la loi (pratique commerciale trompeuse) et se repère vite. Tant que la liste est vide, la section n''apparaît pas sur le site. N''indiquer que le prénom et l''initiale du nom : le témoignage reste crédible sans exposer l''identité complète du client.",
    "_source": "Repris de la page Facebook, où l''avis est public. Prévenir la personne avant de publier le sien : c''est la moindre des politesses, et cela évite toute contestation.",
    "avis": "@avis"
  },
  "config": {
    "_lisezmoi": "Réglages généraux du site. Modifiable depuis admin.html (onglet Réglages).",
    "entreprise": "Le Paille en Queue",
    "baseline": "Spécialités créoles",
    "gerante": "Karine Danna",
    "creation": 2009,
    "telephone": "@reglage:telephone",
    "telephoneLien": "@reglage:telephone_lien",
    "email": "@reglage:email",
    "villeAffichee": "@reglage:ville_affichee",
    "departement": "Dordogne",
    "adresseLegale": "26 Passage de la Forge, 24610 Montpeyroux",
    "siret": "51134341000037",
    "rcs": "RCS Périgueux",
    "ape": "4789Z",
    "minimumParts": "@reglage:minimum_parts",
    "acompte": 30,
    "validiteDevis": "1 mois",
    "delaiCommande": "4 à 5 jours",
    "rayonLivraisonKm": "@reglage:rayon_livraison_km",
    "fraisLivraisonProche": "@reglage:frais_livraison_proche",
    "fraisLivraisonLoin": "@reglage:frais_livraison_loin",
    "seuilCuisineSurPlace": 50,
    "_nonCompris": "Jamais inclus dans les prix : facturés en supplément si le client les demande.",
    "nonCompris": [
      "Service",
      "Vaisselle",
      "Pain"
    ],
    "_endpoint": "Laisser vide tant que le formulaire n''est pas branché : les demandes partiront alors par e-mail via le logiciel de messagerie du client. Voir GUIDE.md, section « Recevoir les demandes de devis ».",
    "formulaireEndpoint": "https://formspree.io/f/mkodyzaq",
    "_champsCaches": "Champs ajoutés à l''envoi, exigés par certains services (Web3Forms réclame par exemple une clé access_key).",
    "formulaireChampsCaches": {},
    "_newsletter": "Adresse d''inscription fournie par Brevo, Mailchimp ou équivalent. Laissée vide, l''inscription part par e-mail via la messagerie du visiteur.",
    "newsletterEndpoint": "https://70e05055.sibforms.com/serve/MUIFADjifzPYLIjxN-H1IJPFoWYLBqkfGZqZ6GOCGmqwsBW2x1J9wGRRQZnxQcL-xYCtr6HEmqylsjqBxD-lEYyrZ6WvRUW-QAZO0Zm_BYLx8v3mzKE3aPoSF5744WrWKWCLucThisU4fYJKNQKTZMnvki6kPL-_L4toeRFhLvnAm_PmPQU83pzMkEXQCTAG8A5z43lazM0zCT0hZQ==",
    "_reseaux": "Laisser vide pour masquer le lien.",
    "facebook": "@reglage:facebook",
    "instagram": "@reglage:instagram",
    "_referencementLocal": "Utilisés uniquement par outils/generer-html.py pour les données structurées. Laissés vides, les champs correspondants sont simplement omis : rien ne casse. La fiche Google et les coordonnées GPS sont les deux signaux les plus utiles pour apparaître dans les recherches locales. Le lien de la fiche est construit sur son identifiant Google (cid) : c''est la forme la plus stable, elle ne casse pas si le nom change.",
    "googleBusinessProfile": "@reglage:google_business_profile",
    "latitude": "45.0567094",
    "longitude": "0.0936312",
    "_avisChiffres": "Chiffres affichés au-dessus des témoignages, sur l''accueil. À reporter à la main depuis Google et Facebook, de temps en temps. Ne jamais gonfler : c''est vérifiable en un clic par le visiteur, et c''est puni par la loi.",
    "avisGoogleNote": "@reglage:avis_google_note",
    "avisGoogleNombre": "@reglage:avis_google_nombre",
    "avisFacebookTaux": "@reglage:avis_facebook_taux",
    "avisFacebookNombre": "@reglage:avis_facebook_nombre",
    "abonnesFacebook": "@reglage:abonnes_facebook",
    "_whatsapp": "Numéro au format international sans espaces ni +, utilisé pour les liens wa.me.",
    "whatsapp": "33627352328",
    "_garanties": "Mentions de sérieux affichées aux professionnels.",
    "haccp": true,
    "assuranceRcPro": true,
    "_newsletterChamps": "Brevo attend un champ nommé EMAIL et quelques champs cachés (email_address_check est le piège à robots : il doit rester vide). Adapter ici selon le service choisi.",
    "newsletterChampEmail": "EMAIL",
    "newsletterChampsCaches": {
      "email_address_check": "",
      "locale": "fr",
      "html_type": "simple"
    },
    "_apave": "Contrôle d''hygiène réalisé par un organisme tiers. Laisser vide pour ne rien afficher.",
    "controleOrganisme": "APAVE",
    "controleVille": "Bordeaux",
    "controleAnnee": "2026",
    "controleResultat": "très satisfaisant"
  }
}'::json);

-- --------------------------------------------------------------------------
-- Contrôle : les comptes attendus
-- --------------------------------------------------------------------------
--   produits 22 · menus 3 · lignes de menu 28 · marchés 5 · avis 1
--
--   select 'produits' t, count(*) from produits
--   union all select 'menus', count(*) from menus
--   union all select 'menu_lignes', count(*) from menu_lignes
--   union all select 'marches', count(*) from marches
--   union all select 'avis', count(*) from avis
--   union all select 'reglages', count(*) from reglages;

