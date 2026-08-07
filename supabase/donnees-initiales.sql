-- ==========================================================================
-- Le Paille en Queue - import initial
-- ==========================================================================
--
-- Fichier engendre par outils/generer-seed-supabase.py.
-- Ne pas le modifier a la main : modifier data/*.json et relancer.
--
-- A executer dans l'editeur SQL de Supabase, apres schema.sql.
-- Re-executable : les tables sont videes avant remplissage.
--
-- Ce fichier est en pur ASCII, commentaires compris. Le trajet
-- presse-papiers puis navigateur peut reinterpreter l'UTF-8 en chemin,
-- et "Reunion" arriverait en base abime, sans erreur pour le dire.
-- Les accents sont donc ecrits en \uXXXX et decodes par PostgreSQL.
-- ==========================================================================

-- "cascade" vide aussi menu_lignes, qui reference menus.
truncate menu_lignes, menus, produits, marches, avis, reglages cascade;

-- --------------------------------------------------------------------------
-- Produits (22)
-- --------------------------------------------------------------------------
insert into produits (famille, slug, nom, description, prix, unite, categorie, vedette, ordre, actif) values
  ('plat', 'rougail-saucisses', 'Rougail saucisses', E'Le plat du dimanche \u00e0 La R\u00e9union. Saucisses fum\u00e9es mijot\u00e9es longuement dans une sauce tomate parfum\u00e9e au gingembre, au curcuma, \u00e0 l''oignon et au thym.', 10, null, 'porc', true, 0, true),
  ('plat', 'rougail-morue', 'Rougail morue', E'Morue dessal\u00e9e et effeuill\u00e9e, tomates fra\u00eeches, oignons et gingembre. Un classique cr\u00e9ole franc et iod\u00e9.', 12, null, 'mer', false, 1, true),
  ('plat', 'cari-poulet', 'Cari poulet', E'Le cari de base de la cuisine r\u00e9unionnaise : poulet dor\u00e9 puis mijot\u00e9 avec oignon, ail, gingembre, curcuma et tomate.', 10, null, 'volaille', false, 2, true),
  ('plat', 'poulet-massale', E'Poulet massal\u00e9', E'Poulet au massal\u00e9, le m\u00e9lange d''\u00e9pices grill\u00e9es de l''oc\u00e9an Indien : coriandre, cumin, girofle, cannelle. Chaleureux et tr\u00e8s parfum\u00e9.', 10, null, 'volaille', true, 3, true),
  ('plat', 'poulet-coco', 'Poulet coco', E'Poulet fondant au lait de coco, adouci par les \u00e9pices. Le plat qui met tout le monde d''accord, y compris les enfants.', 10, null, 'volaille', false, 4, true),
  ('plat', 'poulet-ananas', 'Poulet ananas', E'Sucr\u00e9-sal\u00e9 cr\u00e9ole : poulet mijot\u00e9 et ananas caram\u00e9lis\u00e9. Surprenant et redoutablement efficace en buffet.', 10, null, 'volaille', false, 5, true),
  ('plat', 'poulet-colombo', 'Poulet colombo', E'Poulet au colombo, \u00e9pice des Antilles adopt\u00e9e dans tout l''oc\u00e9an Indien. Rond, doux, l\u00e9g\u00e8rement acidul\u00e9.', 10, null, 'volaille', false, 6, true),
  ('plat', 'curry-dinde', 'Curry de dinde', E'Dinde mijot\u00e9e au curry, une viande l\u00e9g\u00e8re qui passe tr\u00e8s bien en repas d''entreprise et en grande tabl\u00e9e.', 10, null, 'volaille', false, 7, true),
  ('plat', 'porc-colombo', 'Porc colombo', E'\u00c9chine de porc mijot\u00e9e au colombo jusqu''\u00e0 s''effilocher, dans une sauce g\u00e9n\u00e9reuse.', 10, null, 'porc', false, 8, true),
  ('plat', 'porc-ananas', 'Porc ananas', E'Porc caram\u00e9lis\u00e9 \u00e0 l''ananas, l''accord sucr\u00e9-sal\u00e9 qui fait la signature de la cuisine des \u00eeles.', 10, null, 'porc', false, 9, true),
  ('plat', 'lentilles-boucane', E'Lentilles boucan\u00e9', E'Lentilles fondantes et poitrine de porc fum\u00e9e au bois : le boucan\u00e9. Le plat r\u00e9unionnais le plus r\u00e9confortant qui soit.', 10, null, 'porc', false, 10, true),
  ('plat', 'boeuf-massale', E'B\u0153uf massal\u00e9', E'B\u0153uf longuement mijot\u00e9 au massal\u00e9, jusqu''\u00e0 ce que la viande se d\u00e9fasse \u00e0 la cuill\u00e8re.', 10, null, 'boeuf-agneau', true, 11, true),
  ('plat', 'cari-agneau', 'Cari d''agneau', E'Agneau en cari, relev\u00e9 de gingembre frais et de curcuma. Une valeur s\u00fbre pour les repas de f\u00eate.', 12, null, 'boeuf-agneau', false, 12, true),
  ('plat', 'cari-poisson-crevettes', 'Cari poisson ou crevettes', E'Cari de poisson (espadon selon arrivage) ou de crevettes, mont\u00e9 sur un massal\u00e9 l\u00e9ger pour ne pas couvrir le produit.', 12, null, 'mer', true, 13, true),
  ('plat', 'crevettes-coco', 'Crevettes coco', E'Crevettes nacr\u00e9es dans un lait de coco parfum\u00e9 au combava et au gingembre. Le plat le plus demand\u00e9 sur les buffets.', 12, null, 'mer', true, 14, true),
  ('entree', 'samoussas', 'Samoussas', E'Pli\u00e9s et frits \u00e0 la commande. Six garnitures : thon, porc, poulet, poisson, fromage et v\u00e9gan.', 1, E'la pi\u00e8ce', null, true, 0, true),
  ('entree', 'accras-morue', 'Accras de morue', E'Beignets de morue moelleux au c\u0153ur, croustillants dehors. Ils ne survivent jamais longtemps \u00e0 l''ap\u00e9ritif.', 7, 'les 16', null, true, 1, true),
  ('entree', 'bouchons', 'Bouchons', E'Les petites bouch\u00e9es vapeur r\u00e9unionnaises, h\u00e9ritage chinois de l''\u00eele. Servies avec leur sauce.', 5, 'les 6', null, true, 2, true),
  ('boisson', 'punch-planteur', 'Punch planteur', E'Notre planteur maison, pr\u00e9par\u00e9 la veille pour que les fruits aient le temps de parfumer le rhum.', 12, 'le litre', null, false, 0, true),
  ('supplement', 'pain', 'Pain', E'Pain frais du jour, compt\u00e9 par convive.', 1, 'par personne', null, false, 0, true),
  ('supplement', 'vaisselle', 'Vaisselle', 'Assiettes et couverts en carton et en bois. Solide, propre et compostable.', 0.4, 'par personne', null, false, 1, true),
  ('supplement', 'service', E'Service \u00e0 table', E'Une ou plusieurs personnes pour dresser, servir et d\u00e9barrasser. Chiffr\u00e9 selon la dur\u00e9e et le nombre de convives.', null, 'sur devis', null, false, 2, true);

-- --------------------------------------------------------------------------
-- Menus (3) et leur composition (28 lignes)
-- --------------------------------------------------------------------------
insert into menus (slug, nom, resume, prix, prix_max, supplement_motif, ordre, actif) values
  ('menu-creole', E'Menu Cr\u00e9ole', E'L''essentiel de la table r\u00e9unionnaise, en trois services.', 18, null, null, 0, true),
  ('menu-lagon', 'Menu Lagon', E'Une entr\u00e9e \u00e0 l''assiette et des plats plus g\u00e9n\u00e9reux : le menu des grandes occasions.', 24, 26, 'avec un plat poisson, crevettes ou morue', 1, true),
  ('menu-volcan', 'Menu Volcan', 'Notre menu le plus abouti, construit autour des produits les plus nobles de la carte.', 28, 30, 'avec un plat poisson, crevettes ou morue', 2, true);

insert into menu_lignes (menu_id, bloc, libelle, ordre) values
  ((select id from menus where slug = 'menu-creole'), 'entree', 'Salade d''accras de morue', 0),
  ((select id from menus where slug = 'menu-creole'), 'entree', '2 samoussas au choix', 1),
  ((select id from menus where slug = 'menu-creole'), 'plat', 'Cari poisson ou crevettes', 0),
  ((select id from menus where slug = 'menu-creole'), 'plat', E'Poulet coco, ananas, massal\u00e9 ou colombo', 1),
  ((select id from menus where slug = 'menu-creole'), 'plat', 'Porc, dinde ou rougail saucisses', 2),
  ((select id from menus where slug = 'menu-creole'), 'dessert', 'Salade de fruits de saison', 0),
  ((select id from menus where slug = 'menu-creole'), 'inclus', 'Riz et sauce piquante', 0),
  ((select id from menus where slug = 'menu-lagon'), 'entree', E'Assiette de brochettes de crevettes \u00e0 la plancha', 0),
  ((select id from menus where slug = 'menu-lagon'), 'entree', '2 samoussas au choix', 1),
  ((select id from menus where slug = 'menu-lagon'), 'entree', 'Accras de morue', 2),
  ((select id from menus where slug = 'menu-lagon'), 'plat', 'Poulet colombo', 0),
  ((select id from menus where slug = 'menu-lagon'), 'plat', 'Curry de dinde', 1),
  ((select id from menus where slug = 'menu-lagon'), 'plat', E'B\u0153uf massal\u00e9', 2),
  ((select id from menus where slug = 'menu-lagon'), 'plat', 'Crevettes coco', 3),
  ((select id from menus where slug = 'menu-lagon'), 'plat', 'Cari d''agneau', 4),
  ((select id from menus where slug = 'menu-lagon'), 'dessert', 'Salade de fruits exotiques selon la saison', 0),
  ((select id from menus where slug = 'menu-lagon'), 'dessert', E'Part de g\u00e2teau', 1),
  ((select id from menus where slug = 'menu-lagon'), 'inclus', 'Riz et sauce piquante', 0),
  ((select id from menus where slug = 'menu-volcan'), 'entree', 'Crevettes coco', 0),
  ((select id from menus where slug = 'menu-volcan'), 'entree', '2 samoussas au choix', 1),
  ((select id from menus where slug = 'menu-volcan'), 'entree', 'Accras de morue', 2),
  ((select id from menus where slug = 'menu-volcan'), 'plat', E'B\u0153uf massal\u00e9', 0),
  ((select id from menus where slug = 'menu-volcan'), 'plat', 'Cari d''agneau', 1),
  ((select id from menus where slug = 'menu-volcan'), 'plat', 'Cari crevettes ou poisson (espadon)', 2),
  ((select id from menus where slug = 'menu-volcan'), 'plat', E'Curry de dinde aux c\u00e8pes', 3),
  ((select id from menus where slug = 'menu-volcan'), 'dessert', 'Salade de fruits de saison', 0),
  ((select id from menus where slug = 'menu-volcan'), 'dessert', E'Part de g\u00e2teau', 1),
  ((select id from menus where slug = 'menu-volcan'), 'inclus', 'Riz et sauce piquante', 0);

-- --------------------------------------------------------------------------
-- Marches (5)
-- --------------------------------------------------------------------------
insert into marches (lieu, jour, type, horaire, details, jusquau, ordre, actif) values
  ('Le Pizou', 'mardi', 'nocturne', E'\u00c0 partir de 19 h', E'March\u00e9 nocturne d''\u00e9t\u00e9', '2026-08-31', 0, true),
  ('Saint-Laurent-des-Hommes', 'mercredi', 'nocturne', E'\u00c0 partir de 19 h', E'March\u00e9 nocturne d''\u00e9t\u00e9', '2026-08-17', 1, true),
  ('Communes variables', 'vendredi', 'nocturne', E'\u00c0 partir de 19 h', 'La commune change chaque semaine : appelez-nous ou consultez notre page Facebook.', null, 2, true),
  ('Communes variables', 'samedi', 'nocturne', E'\u00c0 partir de 19 h', 'La commune change chaque semaine : appelez-nous ou consultez notre page Facebook.', null, 3, true),
  ('Saint-Seurin-sur-l''Isle', 'dimanche', 'matin', '', '', null, 4, true);

-- --------------------------------------------------------------------------
-- Avis (1)
-- --------------------------------------------------------------------------
insert into avis (auteur, note, contexte, texte, publie, ordre) values
  (E'Ang\u00e8le M.', 5, 'Avis Facebook, avril 2026', E'Ayant des racines cr\u00e9oles, c''est de loin le seul endroit o\u00f9 on se croit \u00e0 La R\u00e9union quand on mange leurs plats. Je recommande \u00e0 200 %, et en plus la sympathie pour aller avec. Bref : au top.', true, 0);

-- --------------------------------------------------------------------------
-- Reglages - ligne unique, gabarits compris
-- --------------------------------------------------------------------------
insert into reglages (telephone, telephone_lien, email, ville_affichee, minimum_parts, frais_livraison_proche, frais_livraison_loin, rayon_livraison_km, facebook, instagram, google_business_profile, avis_google_note, avis_google_nombre, avis_facebook_taux, avis_facebook_nombre, abonnes_facebook, gabarits) values
  ('06 27 35 23 28', '+33627352328', 'contact@lepaille-en-queue.fr', 'Montpeyroux (24)', 10, 5, 10, 50, 'https://www.facebook.com/share/1FLfRCbbv9/?mibextid=wwXIfr', '', 'https://www.google.com/maps?cid=13538170108796715746', '5,0', '4', '100 %', '29', '2 900', '{
  "carte": {
    "_lisezmoi": "La carte compl\u00e8te. Modifiable depuis admin.html (onglet Carte). Les prix sont en euros, par part. Le champ \u00ab image \u00bb pointe vers images/<nom-du-fichier> : tant que le fichier n''existe pas, le site affiche un joli aplat color\u00e9 \u00e0 la place.",
    "mentionPart": "Tous les plats sont servis avec le riz et la sauce piquante.",
    "mentionMinimum": "Commande \u00e0 partir de 10 parts.",
    "mentionNonCompris": "Le service, la vaisselle et le pain ne sont jamais compris dans nos prix. Pain 1 \u20ac et vaisselle 0,40 \u20ac par personne, service sur devis.",
    "mentionLivraison": "Nous nous d\u00e9pla\u00e7ons jusqu''\u00e0 50 km autour de Montpeyroux : livraison 5 \u20ac jusqu''\u00e0 10 km, 10 \u20ac au-del\u00e0. Plus loin, sur devis.",
    "mentionDelai": "Commande \u00e0 passer 4 \u00e0 5 jours \u00e0 l''avance.",
    "mentionAutresCuisines": "La carte ci-dessous est notre sp\u00e9cialit\u00e9. Pour un \u00e9v\u00e9nement, nous composons aussi des repas plus classiques, ou un menu qui m\u00eale les deux : parlez-nous de vos invit\u00e9s.",
    "plats": "@produits:plat",
    "entrees": "@produits:entree",
    "buffet": {
      "titre": "En buffet",
      "texte": "Pour un cocktail, un vin d''honneur ou une inauguration, nous composons un buffet cr\u00e9ole \u00e0 partager.",
      "elements": [
        "Bouchons",
        "Samoussas",
        "Accras de morue",
        "Boudins cr\u00e9oles",
        "Brochettes tomate-fromage",
        "Brochettes de crevettes \u00e0 la plancha"
      ]
    },
    "_supplements": "Prestations jamais comprises dans les prix, factur\u00e9es en plus si le client les demande. Un prix \u00e0 null s''affiche \u00ab sur devis \u00bb.",
    "supplements": "@produits:supplement",
    "boissons": "@produits:boisson",
    "menus": "@menus"
  },
  "marches": {
    "_lisezmoi": "Les march\u00e9s o\u00f9 Karine est pr\u00e9sente. Modifiable depuis admin.html (onglet March\u00e9s). \u00ab jour \u00bb : lundi\u2026dimanche pour un march\u00e9 hebdomadaire, ou une date au format AAAA-MM-JJ pour une date unique. \u00ab type \u00bb : matin ou nocturne. \u00ab jusquau \u00bb (facultatif, AAAA-MM-JJ) borne un march\u00e9 de saison : pass\u00e9e cette date, il dispara\u00eet tout seul de la page. Tant que la liste est vide, la page affiche une invitation \u00e0 t\u00e9l\u00e9phoner.",
    "marches": "@marches"
  },
  "avis": {
    "_lisezmoi": "T\u00e9moignages de clients. Modifiable depuis admin.html (onglet Avis). N''y mettre que de VRAIS avis, avec l''accord de la personne : un faux t\u00e9moignage est interdit par la loi (pratique commerciale trompeuse) et se rep\u00e8re vite. Tant que la liste est vide, la section n''appara\u00eet pas sur le site. N''indiquer que le pr\u00e9nom et l''initiale du nom : le t\u00e9moignage reste cr\u00e9dible sans exposer l''identit\u00e9 compl\u00e8te du client.",
    "_source": "Repris de la page Facebook, o\u00f9 l''avis est public. Pr\u00e9venir la personne avant de publier le sien : c''est la moindre des politesses, et cela \u00e9vite toute contestation.",
    "avis": "@avis"
  },
  "config": {
    "_lisezmoi": "R\u00e9glages g\u00e9n\u00e9raux du site. Modifiable depuis admin.html (onglet R\u00e9glages).",
    "entreprise": "Le Paille en Queue",
    "baseline": "Sp\u00e9cialit\u00e9s cr\u00e9oles",
    "gerante": "Karine Danna",
    "creation": 2009,
    "telephone": "@reglage:telephone",
    "telephoneLien": "@reglage:telephone_lien",
    "email": "@reglage:email",
    "villeAffichee": "@reglage:ville_affichee",
    "departement": "Dordogne",
    "adresseLegale": "26 Passage de la Forge, 24610 Montpeyroux",
    "siret": "51134341000037",
    "rcs": "RCS P\u00e9rigueux",
    "ape": "4789Z",
    "minimumParts": "@reglage:minimum_parts",
    "acompte": 30,
    "validiteDevis": "1 mois",
    "delaiCommande": "4 \u00e0 5 jours",
    "rayonLivraisonKm": "@reglage:rayon_livraison_km",
    "fraisLivraisonProche": "@reglage:frais_livraison_proche",
    "fraisLivraisonLoin": "@reglage:frais_livraison_loin",
    "seuilCuisineSurPlace": 50,
    "_nonCompris": "Jamais inclus dans les prix : factur\u00e9s en suppl\u00e9ment si le client les demande.",
    "nonCompris": [
      "Service",
      "Vaisselle",
      "Pain"
    ],
    "_endpoint": "Laisser vide tant que le formulaire n''est pas branch\u00e9 : les demandes partiront alors par e-mail via le logiciel de messagerie du client. Voir GUIDE.md, section \u00ab Recevoir les demandes de devis \u00bb.",
    "formulaireEndpoint": "https://formspree.io/f/mkodyzaq",
    "_champsCaches": "Champs ajout\u00e9s \u00e0 l''envoi, exig\u00e9s par certains services (Web3Forms r\u00e9clame par exemple une cl\u00e9 access_key).",
    "formulaireChampsCaches": {},
    "_carnet": "Carnet de commandes : les demandes de devis sont aussi consign\u00e9es dans Supabase, en plus de l''e-mail. Ces deux valeurs sont publiques \u2014 la cl\u00e9 n''autorise que le d\u00e9p\u00f4t d''une demande, jamais sa lecture. Vider pour ne plus rien consigner.",
    "supabaseUrl": "https://ktdlmdidtfptkudrnyzi.supabase.co",
    "supabaseClePublique": "sb_publishable_mmyRoaBrbSWEMPpcHziPJg_aWXBBWVX",
    "_newsletter": "Adresse d''inscription fournie par Brevo, Mailchimp ou \u00e9quivalent. Laiss\u00e9e vide, l''inscription part par e-mail via la messagerie du visiteur.",
    "newsletterEndpoint": "https://70e05055.sibforms.com/serve/MUIFADjifzPYLIjxN-H1IJPFoWYLBqkfGZqZ6GOCGmqwsBW2x1J9wGRRQZnxQcL-xYCtr6HEmqylsjqBxD-lEYyrZ6WvRUW-QAZO0Zm_BYLx8v3mzKE3aPoSF5744WrWKWCLucThisU4fYJKNQKTZMnvki6kPL-_L4toeRFhLvnAm_PmPQU83pzMkEXQCTAG8A5z43lazM0zCT0hZQ==",
    "_reseaux": "Laisser vide pour masquer le lien.",
    "facebook": "@reglage:facebook",
    "instagram": "@reglage:instagram",
    "_referencementLocal": "Utilis\u00e9s uniquement par outils/generer-html.py pour les donn\u00e9es structur\u00e9es. Laiss\u00e9s vides, les champs correspondants sont simplement omis : rien ne casse. La fiche Google et les coordonn\u00e9es GPS sont les deux signaux les plus utiles pour appara\u00eetre dans les recherches locales. Le lien de la fiche est construit sur son identifiant Google (cid) : c''est la forme la plus stable, elle ne casse pas si le nom change.",
    "googleBusinessProfile": "@reglage:google_business_profile",
    "latitude": "45.0567094",
    "longitude": "0.0936312",
    "_avisChiffres": "Chiffres affich\u00e9s au-dessus des t\u00e9moignages, sur l''accueil. \u00c0 reporter \u00e0 la main depuis Google et Facebook, de temps en temps. Ne jamais gonfler : c''est v\u00e9rifiable en un clic par le visiteur, et c''est puni par la loi.",
    "avisGoogleNote": "@reglage:avis_google_note",
    "avisGoogleNombre": "@reglage:avis_google_nombre",
    "avisFacebookTaux": "@reglage:avis_facebook_taux",
    "avisFacebookNombre": "@reglage:avis_facebook_nombre",
    "abonnesFacebook": "@reglage:abonnes_facebook",
    "_whatsapp": "Num\u00e9ro au format international sans espaces ni +, utilis\u00e9 pour les liens wa.me.",
    "whatsapp": "33627352328",
    "_garanties": "Mentions de s\u00e9rieux affich\u00e9es aux professionnels.",
    "haccp": true,
    "assuranceRcPro": true,
    "_newsletterChamps": "Brevo attend un champ nomm\u00e9 EMAIL et quelques champs cach\u00e9s (email_address_check est le pi\u00e8ge \u00e0 robots : il doit rester vide). Adapter ici selon le service choisi.",
    "newsletterChampEmail": "EMAIL",
    "newsletterChampsCaches": {
      "email_address_check": "",
      "locale": "fr",
      "html_type": "simple"
    },
    "_apave": "Contr\u00f4le d''hygi\u00e8ne r\u00e9alis\u00e9 par un organisme tiers. Laisser vide pour ne rien afficher.",
    "controleOrganisme": "APAVE",
    "controleVille": "Bordeaux",
    "controleAnnee": "2026",
    "controleResultat": "tr\u00e8s satisfaisant"
  }
}'::json);

-- --------------------------------------------------------------------------
-- Controle : les comptes attendus
-- --------------------------------------------------------------------------
--   produits 22 | menus 3 | lignes de menu 28 | marches 5 | avis 1
--
--   select 'produits' t, count(*) from produits
--   union all select 'menus', count(*) from menus
--   union all select 'menu_lignes', count(*) from menu_lignes
--   union all select 'marches', count(*) from marches
--   union all select 'avis', count(*) from avis
--   union all select 'reglages', count(*) from reglages;

