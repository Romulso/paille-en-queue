/* =========================================================
   Le Paille en Queue — comportements du site
   Aucune dépendance : le site fonctionne en ouvrant les fichiers
   tels quels. Le contenu vit dans data/*.json.
   ========================================================= */
(() => {
  "use strict";

  const $ = (sel, racine = document) => racine.querySelector(sel);
  const $$ = (sel, racine = document) => [...racine.querySelectorAll(sel)];

  // 10 → « 10 € », 0.4 → « 0,40 € », null → « sur devis ».
  const euros = (n) => {
    if (n === null || n === undefined) return "sur devis";
    return Number.isInteger(n)
      ? `${n} €`
      : `${n.toLocaleString("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €`;
  };
  const echapper = (s) => String(s).replace(/[&<>"]/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  async function charger(nom) {
    try {
      const r = await fetch(`data/${nom}.json`, { cache: "no-cache" });
      if (!r.ok) throw new Error(r.status);
      return await r.json();
    } catch (e) {
      console.warn(`Impossible de charger data/${nom}.json`, e);
      return null;
    }
  }

  /* ---------- Réglages appliqués au HTML ----------
     Le HTML contient déjà les bonnes valeurs (le site reste lisible
     sans JavaScript) ; on les rafraîchit si config.json a changé. */
  async function appliquerConfig() {
    const cfg = await charger("config");
    if (!cfg) return null;
    $$("[data-cfg]").forEach((el) => {
      const v = cfg[el.dataset.cfg];
      if (v !== undefined && v !== "" && el.textContent.trim() !== String(v)) {
        el.textContent = v;
      }
    });
    $$("[data-cfg-href]").forEach((el) => {
      const [cle, prefixe = ""] = el.dataset.cfgHref.split("|");
      if (cfg[cle]) el.href = prefixe + cfg[cle];
    });
    // L'ancienneté se calcule, elle ne s'écrit pas : « quinze ans » figé dans
    // le HTML devient faux au bout d'un an, et personne ne le relit jamais.
    if (cfg.creation) {
      const ans = new Date().getFullYear() - cfg.creation;
      const LETTRES = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six",
        "sept", "huit", "neuf", "dix", "onze", "douze", "treize", "quatorze",
        "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf", "vingt",
        "vingt et un", "vingt-deux", "vingt-trois", "vingt-quatre", "vingt-cinq"];
      const enLettres = LETTRES[ans] || String(ans);
      const majuscule = enLettres.charAt(0).toUpperCase() + enLettres.slice(1);
      $$("[data-anciennete]").forEach((el) => { el.textContent = majuscule; });
    }

    // Réseaux sociaux : on masque le lien tant qu'aucune adresse n'est renseignée.
    $$("[data-reseau]").forEach((el) => {
      const url = cfg[el.dataset.reseau];
      if (url) { el.href = url; el.hidden = false; } else { el.hidden = true; }
    });
    return cfg;
  }

  /* ---------- En-tête ---------- */
  function entete() {
    const entete = $(".entete");
    const burger = $(".burger");
    const menu = $(".menu-mobile");

    if (entete) {
      const surveiller = () => entete.classList.toggle("est-collee", window.scrollY > 8);
      surveiller();
      addEventListener("scroll", surveiller, { passive: true });
    }

    if (burger && menu) {
      burger.addEventListener("click", () => {
        const ouvert = burger.getAttribute("aria-expanded") === "true";
        burger.setAttribute("aria-expanded", String(!ouvert));
        menu.classList.toggle("est-ouvert", !ouvert);
      });
      menu.addEventListener("click", (e) => {
        if (e.target.closest("a")) {
          burger.setAttribute("aria-expanded", "false");
          menu.classList.remove("est-ouvert");
        }
      });
    }

    // Marque la page courante dans les deux menus.
    // L'accueil s'écrit « / » dans les liens (l'URL canonique) mais
    // « index.html » dans un chemin de fichier : on ramène les deux à la même
    // forme, sinon la page d'accueil ne serait jamais marquée comme courante.
    const normaliser = (chemin) => {
      const dernier = chemin.split("/").pop();
      return dernier === "" || dernier === "index.html" ? "/" : dernier;
    };
    const ici = normaliser(location.pathname);
    $$(".nav a, .menu-mobile a").forEach((a) => {
      const cible = (a.getAttribute("href") || "").split("#")[0];
      if (cible && normaliser(cible) === ici) a.setAttribute("aria-current", "page");
    });
  }

  /* ---------- Photos ----------
     Tant qu'une photo n'a pas été déposée dans images/, on affiche un
     aplat coloré portant le nom du plat plutôt qu'une image cassée. */
  function replisPhoto(racine = document) {
    // La photo de bannière est un bonus : sans elle, le dégradé suffit.
    $$(".heros-photo", racine).forEach((img) => {
      img.addEventListener("error", () => img.remove());
      if (img.complete && img.naturalWidth === 0) img.remove();
    });
    // Chaque cadre reçoit sa teinte tout de suite : l'aplat est prêt bien
    // avant que l'image ne se charge, ou n'échoue à se charger.
    $$(".photo", racine).forEach((cadre) => {
      if (/(^| )t[1-8]( |$)/.test(cadre.className)) return;
      const nom = cadre.dataset.nom || "";
      let somme = 0;
      for (const c of nom) somme += c.charCodeAt(0);
      cadre.classList.add(`t${(somme % 8) + 1}`);
    });
    // Une image absente est retirée pour ne pas laisser l'icône « cassée ».
    $$(".photo img", racine).forEach((img) => {
      img.addEventListener("error", () => echecPhoto(img));
      if (img.complete && img.naturalWidth === 0) echecPhoto(img);
    });
  }

  /* Une photo qui ne se charge pas mérite une seconde chance avant d'être
     retirée : dans un <picture>, le navigateur s'engage sur la première source
     dont le type lui convient et n'essaie pas les suivantes. Si le .avif n'a
     pas été généré alors que le .jpg existe — un oubli de
     outils/optimiser-images.py — la photo disparaîtrait pour rien. On enlève
     donc les sources et on laisse le JPEG tenter sa chance. */
  function echecPhoto(img) {
    const pere = img.parentElement;
    if (pere && pere.tagName === "PICTURE" && pere.querySelector("source")) {
      $$("source", pere).forEach((s) => s.remove());
      const adresse = img.getAttribute("src");
      img.removeAttribute("src");
      img.setAttribute("src", adresse);
      return;
    }
    img.remove();
  }

  /* ---------- Apparition au défilement ---------- */
  function toutMontrer() {
    $$(".apparait").forEach((el) => el.classList.add("est-vu"));
  }

  function apparitions() {
    const cibles = $$(".apparait:not(.est-vu)");
    if (!cibles.length) return;
    if (!("IntersectionObserver" in window)) { toutMontrer(); return; }

    const obs = new IntersectionObserver((entrees) => {
      entrees.forEach((e) => {
        if (!e.isIntersecting) return;
        e.target.classList.add("est-vu");
        obs.unobserve(e.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    cibles.forEach((el) => obs.observe(el));

    // Filet de sécurité : l'observateur ne se déclenche pas quand l'onglet
    // est masqué. Passé ce délai, on affiche tout plutôt que rien.
    clearTimeout(apparitions.minuteur);
    apparitions.minuteur = setTimeout(toutMontrer, 2500);
  }

  /* ---------- Gabarits ---------- */
  function gabaritPlat(p, unite = "la part") {
    return `
      <article class="plat apparait" data-categorie="${echapper(p.categorie || "")}">
        <div class="photo" data-nom="${echapper(p.nom)}">
          ${p.vedette ? '<span class="etiquette-vedette">Signature</span>' : ""}
          <picture>
            <source type="image/avif" srcset="images/${echapper(p.slug)}.avif">
            <source type="image/webp" srcset="images/${echapper(p.slug)}.webp">
            <img src="images/${echapper(p.slug)}.jpg" alt="${echapper(p.nom)}, plat créole préparé par Le Paille en Queue, traiteur en Dordogne" loading="lazy" decoding="async" width="600" height="450">
          </picture>
        </div>
        <div class="plat-corps">
          <div class="plat-tete">
            <h3>${echapper(p.nom)}</h3>
            <span class="prix">${euros(p.prix)}<small>${echapper(p.unite || unite)}</small></span>
          </div>
          <p>${echapper(p.description)}</p>
        </div>
      </article>`;
  }

  function gabaritFormule(m, vedette) {
    const bloc = (titre, lignes) => !lignes || !lignes.length ? "" : `
      <div class="formule-bloc">
        <h4>${titre}</h4>
        <ul>${lignes.map((l) => `<li>${echapper(l)}</li>`).join("")}</ul>
      </div>`;
    const prix = m.prixMax
      ? `${m.prix} <span>à</span> ${m.prixMax} <span>€</span>`
      : `${m.prix} <span>€</span>`;
    // Le prix haut ne s'applique qu'à certains plats : on dit lesquels,
    // sinon le visiteur suppose le pire et n'ose pas demander.
    const detailPrix = m.prixMax
      ? `par personne — ${m.prixMax} € ${echapper(m.supplementMotif || "selon le plat choisi")}`
      : "par personne";
    return `
      <article class="formule apparait${vedette ? " formule-vedette" : ""}">
        ${vedette ? '<span class="formule-ruban">Le plus demandé</span>' : ""}
        <h3>${echapper(m.nom)}</h3>
        <p class="formule-prix">${prix}<small>${detailPrix}</small></p>
        <p>${echapper(m.resume)}</p>
        ${bloc("Entrée", m.entree)}
        ${bloc("Plat au choix", m.plats)}
        ${bloc("Dessert", m.dessert)}
        ${m.inclus && m.inclus.length
          ? `<p class="formule-inclus">Compris : ${m.inclus.map(echapper).join(" · ")}.</p>` : ""}
        <a class="pastille pastille-pleine" href="devis.html?menu=${encodeURIComponent(m.slug)}">Demander ce menu</a>
      </article>`;
  }

  /* ---------- La carte ---------- */
  async function carte() {
    const zonePlats = $("#zone-plats");
    const zoneVedettes = $("#zone-vedettes");
    const zoneEntrees = $("#zone-entrees");
    const zoneBoissons = $("#zone-boissons");
    const zoneMenus = $("#zone-menus");
    const zoneBuffet = $("#zone-buffet");
    if (!zonePlats && !zoneVedettes && !zoneMenus) return;

    const d = await charger("carte");
    if (!d) return;

    if (zoneVedettes) {
      const mis = [...d.plats, ...d.entrees].filter((p) => p.vedette).slice(0, 6);
      zoneVedettes.innerHTML = mis.map((p) => gabaritPlat(p)).join("");
    }
    if (zonePlats) {
      zonePlats.innerHTML = d.plats.map((p) => gabaritPlat(p)).join("");
      filtres(zonePlats);
    }
    if (zoneEntrees) {
      zoneEntrees.innerHTML = d.entrees.map((p) => gabaritPlat(p)).join("");
    }
    if (zoneBoissons) {
      zoneBoissons.innerHTML = d.boissons.map((p) => gabaritPlat(p)).join("");
    }
    if (zoneMenus) {
      // Le menu du milieu est mis en avant : c'est le plus choisi.
      zoneMenus.innerHTML = d.menus.map((m, i) => gabaritFormule(m, i === 1)).join("");
    }
    if (zoneBuffet && d.buffet) {
      zoneBuffet.innerHTML = d.buffet.elements
        .map((e) => `<li>${echapper(e)}</li>`).join("");
    }
    const zoneSupplements = $("#zone-supplements");
    if (zoneSupplements && d.supplements) {
      zoneSupplements.innerHTML = d.supplements.map((s) => `
        <article class="supplement apparait">
          <h3>${echapper(s.nom)}</h3>
          <span class="prix">${euros(s.prix)}${s.prix === null ? "" : `<small>${echapper(s.unite)}</small>`}</span>
          <p>${echapper(s.description)}</p>
        </article>`).join("");
    }

    // Les mentions commerciales sont écrites en dur dans le HTML (lisibles
    // sans JavaScript) et rafraîchies ici si data/carte.json a changé.
    const mentions = {
      "data-mention-part": d.mentionPart,
      "data-mention-minimum": d.mentionMinimum,
      "data-mention-non-compris": d.mentionNonCompris,
      "data-mention-livraison": d.mentionLivraison,
      "data-mention-delai": d.mentionDelai,
      "data-mention-autres-cuisines": d.mentionAutresCuisines,
    };
    Object.entries(mentions).forEach(([attr, texte]) => {
      if (texte) $$(`[${attr}]`).forEach((el) => { el.textContent = texte; });
    });

    if (zoneMenus) schemaCarte(d);

    replisPhoto();
    apparitions();
  }

  /* Données structurées de la carte, construites à partir du même JSON que
     l'affichage : les prix annoncés à Google ne peuvent pas diverger. */
  function schemaCarte(d) {
    if ($("#schema-carte")) return;
    const article = (p) => ({
      "@type": "MenuItem",
      name: p.nom,
      description: p.description,
      offers: {
        "@type": "Offer",
        price: p.prix,
        priceCurrency: "EUR",
        description: p.unite || "la part",
      },
    });
    const section = (nom, liste) => ({
      "@type": "MenuSection", name: nom, hasMenuItem: liste.map(article),
    });

    const schema = {
      "@context": "https://schema.org",
      "@type": "Menu",
      name: "La carte du Paille en Queue",
      inLanguage: "fr-FR",
      url: "https://lepaille-en-queue.fr/carte.html",
      hasMenuSection: [
        section("Plats créoles", d.plats),
        section("Entrées et apéritif", d.entrees),
        section("Boissons", d.boissons),
        {
          "@type": "MenuSection",
          name: "Menus complets",
          hasMenuItem: d.menus.map((m) => ({
            "@type": "MenuItem",
            name: m.nom,
            description: m.resume,
            offers: {
              "@type": "Offer",
              price: m.prix,
              priceCurrency: "EUR",
              description: m.prixMax
                ? `Par personne, jusqu'à ${m.prixMax} € ${m.supplementMotif || ""}`.trim()
                : "Par personne",
            },
          })),
        },
      ],
    };
    const balise = document.createElement("script");
    balise.type = "application/ld+json";
    balise.id = "schema-carte";
    balise.textContent = JSON.stringify(schema);
    document.head.append(balise);
  }

  function filtres(zone) {
    const barre = $(".barre-filtres");
    if (!barre) return;
    barre.addEventListener("click", (e) => {
      const bouton = e.target.closest(".filtre");
      if (!bouton) return;
      $$(".filtre", barre).forEach((b) => b.setAttribute("aria-pressed", String(b === bouton)));
      const cat = bouton.dataset.categorie;
      $$(".plat", zone).forEach((p) => {
        p.hidden = cat !== "tout" && p.dataset.categorie !== cat;
      });
    });
  }

  /* ---------- Marchés ---------- */
  const JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"];

  // Les marchés hebdomadaires viennent en premier, dans l'ordre de la semaine ;
  // les dates uniques ensuite, par ordre chronologique.
  const rang = (m) => {
    const i = JOURS.indexOf(m.jour);
    return i >= 0 ? i : 100 + Number(String(m.jour).replace(/-/g, ""));
  };

  async function marches() {
    const zone = $("#zone-marches");
    if (!zone) return;
    const d = await charger("marches");
    const tous = d && Array.isArray(d.marches) ? d.marches : [];

    // Un marché de saison disparaît de lui-même passée sa date de fin : mieux
    // vaut une case vide qu'un client qui se déplace pour rien.
    const aujourdhui = new Date().toISOString().slice(0, 10);
    const liste = tous
      .filter((m) => !m.jusquau || m.jusquau >= aujourdhui)
      .sort((a, b) => rang(a) - rang(b));

    if (!liste.length) {
      zone.innerHTML = `
        <div class="etat-vide">
          <h3>Le calendrier arrive</h3>
          <p>Nos dates de marchés pour la saison sont en cours de mise à jour.
             Appelez Karine au <a href="tel:+33627352328"><b>06 27 35 23 28</b></a>
             pour savoir où nous retrouver cette semaine.</p>
        </div>`;
      return;
    }

    zone.className = "grille-marches";
    zone.innerHTML = liste.map((m) => {
      const estDate = /^\d{4}-\d{2}-\d{2}$/.test(m.jour);
      let haut = "", bas = "";
      if (estDate) {
        const d2 = new Date(`${m.jour}T12:00:00`);
        haut = String(d2.getDate());
        bas = d2.toLocaleDateString("fr-FR", { month: "short" });
      } else {
        haut = m.jour.slice(0, 3);
        bas = "chaque semaine";
      }
      return `
        <article class="marche apparait">
          <div class="marche-jour"><b>${echapper(haut)}</b>${echapper(bas)}</div>
          <div>
            <h3>${echapper(m.lieu)}</h3>
            ${m.horaire ? `<p>${echapper(m.horaire)}</p>` : ""}
            ${m.precision ? `<p>${echapper(m.precision)}</p>` : ""}
            ${m.jusquau ? `<p>Jusqu'au ${new Date(`${m.jusquau}T12:00:00`)
              .toLocaleDateString("fr-FR", { day: "numeric", month: "long" })}</p>` : ""}
            <span class="marche-type ${m.type === "nocturne" ? "nocturne" : ""}">
              ${m.type === "nocturne" ? "Marché nocturne" : "Marché du matin"}
            </span>
          </div>
        </article>`;
    }).join("");
    apparitions();
  }

  /* ---------- Avis ---------- */
  async function avis(cfg) {
    const section = $("#section-avis");
    if (!section) return;
    const d = await charger("avis");
    const liste = d && Array.isArray(d.avis) ? d.avis : [];
    section.hidden = false;

    // Pas encore de témoignage : plutôt que de masquer la section ou d'en
    // inventer, on invite les clients à en laisser un.
    if (!liste.length) {
      $("#zone-avis").className = "";
      // Un avis Google vaut bien plus qu'un avis déposé ici : il compte pour le
      // référencement local, et il est vérifiable par le visiteur suivant.
      $("#zone-avis").innerHTML = `
        <div class="etat-vide">
          <h3>Les premiers avis arrivent</h3>
          <p>
            Vous avez fait appel à nous pour un repas ou un événement&nbsp;?
            Votre retour aide énormément les personnes qui hésitent encore.
          </p>
          <p style="margin-top:18px">
            ${cfg && cfg.googleBusinessProfile
              ? `<a class="pastille pastille-pleine" rel="noopener"
                    href="${echapper(cfg.googleBusinessProfile)}">Laisser un avis sur Google</a>`
              : `<a class="pastille pastille-pleine"
                    href="mailto:contact@lepaille-en-queue.fr?subject=${encodeURIComponent("Mon avis sur Le Paille en Queue")}"
                    data-cfg-href="email|mailto:">Laisser un avis</a>`}
          </p>
        </div>`;
      apparitions();
      return;
    }
    $("#zone-avis").className = "grille-avis";

    $("#zone-avis").innerHTML = liste.map((a) => {
      const initiale = (a.auteur || "?").trim().charAt(0).toUpperCase();
      return `
      <article class="avis apparait">
        ${a.note ? `<div class="etoiles" aria-label="${a.note} sur 5">${"★".repeat(a.note)}${"☆".repeat(5 - a.note)}</div>` : ""}
        <p>« ${echapper(a.texte)} »</p>
        <footer>
          <span class="avatar" aria-hidden="true">${echapper(initiale)}</span>
          <span>
            <b>${echapper(a.auteur)}</b>
            ${a.contexte ? `<small>${echapper(a.contexte)}</small>` : ""}
          </span>
        </footer>
      </article>`;
    }).join("");
    apparitions();
  }

  /* ---------- Infolettre ---------- */
  function infolettre(cfg) {
    const form = $("#form-infolettre");
    if (!form) return;
    const etat = $("#infolettre-etat");
    const champ = $("input", form);

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!form.reportValidity()) return;
      const adresse = champ.value.trim();
      const endpoint = (cfg && cfg.newsletterEndpoint) || "";

      if (!endpoint) {
        // Pas de service d'envoi branché : l'inscription part par e-mail.
        const objet = "Inscription à la newsletter";
        const corps = `Bonjour,\n\nJe souhaite recevoir vos actualités à cette adresse : ${adresse}\n`;
        location.href = `mailto:${(cfg && cfg.email) || "contact@lepaille-en-queue.fr"}`
          + `?subject=${encodeURIComponent(objet)}&body=${encodeURIComponent(corps)}`;
        etat.textContent = "Votre messagerie s'ouvre : il ne reste qu'à envoyer.";
        return;
      }

      etat.textContent = "Inscription en cours…";
      // Chaque service impose son nom de champ : Brevo attend EMAIL, Formspree
      // accepte n'importe quoi. Le nom et les champs cachés viennent des réglages.
      const envoi = new FormData();
      envoi.append((cfg && cfg.newsletterChampEmail) || "E-mail", adresse);
      Object.entries((cfg && cfg.newsletterChampsCaches) || {})
        .forEach(([cle, val]) => envoi.append(cle, val));

      try {
        const r = await fetch(endpoint, {
          method: "POST",
          body: envoi,
          headers: { Accept: "application/json" },
          mode: endpoint.includes("sibforms.com") ? "no-cors" : "cors",
        });
        // En mode no-cors la réponse est opaque : pas de statut lisible, mais
        // l'envoi a bien eu lieu. On ne considère un échec que si on peut le lire.
        if (r.type !== "opaque" && !r.ok) throw new Error(r.status);
        form.reset();
        etat.textContent = "C'est noté, merci ! Confirmez l'inscription depuis l'e-mail que vous allez recevoir.";
      } catch (err) {
        console.error(err);
        etat.textContent = "L'inscription n'a pas abouti. Réessayez plus tard.";
      }
    });
  }

  /* ---------- Formulaire de devis ---------- */
  async function devis(cfg) {
    const form = $("#form-devis");
    if (!form) return;

    // Les plats cochables sont générés depuis la carte : une seule source.
    const zone = $("#zone-choix-plats");
    const d = await charger("carte");
    if (zone && d) {
      const ligne = (p) => `
        <label class="choix">
          <input type="checkbox" name="Plats souhaités" value="${echapper(p.nom)}">
          ${echapper(p.nom)} <span class="choix-prix">${euros(p.prix)}</span>
        </label>`;
      zone.innerHTML = d.plats.map(ligne).join("");
      $("#zone-choix-entrees").innerHTML = [...d.entrees, ...d.boissons].map((p) => `
        <label class="choix">
          <input type="checkbox" name="Entrées et boissons" value="${echapper(p.nom)}">
          ${echapper(p.nom)} <span class="choix-prix">${euros(p.prix)} ${echapper(p.unite || "")}</span>
        </label>`).join("");

      // Les suppléments portent leur prix : le client sait ce qu'il coche.
      const zoneSup = $("#zone-choix-supplements");
      if (zoneSup && d.supplements) {
        zoneSup.innerHTML = d.supplements.map((s) => {
          const tarif = s.prix === null ? euros(null) : `${euros(s.prix)} ${s.unite}`;
          return `
          <label class="choix">
            <input type="checkbox" name="Prestations en supplément" value="${echapper(`${s.nom} (${tarif})`)}">
            ${echapper(s.nom)} <span class="choix-prix">${echapper(tarif)}</span>
          </label>`;
        }).join("");
      }

      const selMenu = $("#formule");
      if (selMenu) {
        d.menus.forEach((m) => {
          const o = document.createElement("option");
          o.value = m.nom;
          o.textContent = `${m.nom} — ${m.prixMax ? `${m.prix} à ${m.prixMax}` : m.prix} € par personne`;
          selMenu.append(o);
        });
        // Pré-sélection quand on arrive depuis « Demander ce menu ».
        const voulu = new URLSearchParams(location.search).get("menu");
        if (voulu) {
          const m = d.menus.find((x) => x.slug === voulu);
          if (m) selMenu.value = m.nom;
        }
      }
    }

    // Reprise du formulaire court de l'accueil : on ne redemande pas ce que
    // le visiteur vient de saisir.
    const params = new URLSearchParams(location.search);
    let repris = false;
    [["date", "#date"], ["convives", "#convives"], ["type", "#type"]]
      .forEach(([cle, selecteur]) => {
        const valeur = params.get(cle);
        const champ = $(selecteur);
        if (valeur && champ) { champ.value = valeur; repris = true; }
      });
    if (repris || params.get("menu")) {
      requestAnimationFrame(() => {
        $("#form-devis").scrollIntoView({ block: "start", behavior: "smooth" });
      });
    }

    // La date ne peut pas être dans le passé.
    const champDate = $("#date");
    if (champDate) {
      const demain = new Date(Date.now() + 86400000);
      champDate.min = demain.toISOString().slice(0, 10);
    }

    const messageOK = $("#message-succes");
    const messageKO = $("#message-erreur");
    const bouton = $("#bouton-envoi");

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      messageOK.classList.remove("est-visible");
      messageKO.classList.remove("est-visible");

      if ($("#site-web").value) return;          // piège à robots
      if (!form.reportValidity()) return;

      const donnees = new FormData(form);
      donnees.delete("site-web");
      const endpoint = (cfg && cfg.formulaireEndpoint) || "";

      if (!endpoint) {
        // Pas encore de service d'envoi branché : on bascule sur le
        // logiciel de messagerie du visiteur, sans rien perdre.
        location.href = lienMail(donnees);
        messageOK.textContent = "Votre messagerie vient de s'ouvrir avec la demande pré-remplie. Il ne reste qu'à l'envoyer.";
        messageOK.classList.add("est-visible");
        return;
      }

      // Certains services (Web3Forms…) exigent une clé transmise avec l'envoi.
      Object.entries((cfg && cfg.formulaireChampsCaches) || {})
        .forEach(([cle, val]) => donnees.append(cle, val));

      bouton.disabled = true;
      const libelle = bouton.textContent;
      bouton.textContent = "Envoi en cours…";
      try {
        const r = await fetch(endpoint, {
          method: "POST",
          body: donnees,
          headers: { Accept: "application/json" },
        });
        if (!r.ok) throw new Error(r.status);
        // La demande est partie : on la consigne au carnet, sans attendre et
        // sans que le visiteur ait à s'en soucier.
        consignerDemande(cfg, donnees);
        form.reset();
        messageOK.textContent = "Merci ! Votre demande est bien partie. Karine vous répond sous 48 h avec un devis détaillé.";
        messageOK.classList.add("est-visible");
        messageOK.scrollIntoView({ block: "center", behavior: "smooth" });
      } catch (err) {
        console.error(err);
        messageKO.classList.add("est-visible");
      } finally {
        bouton.disabled = false;
        bouton.textContent = libelle;
      }
    });
  }

  /* Consigne la demande dans le carnet de commandes (Supabase).

     Volontairement après l'envoi par e-mail, et sans jamais faire échouer
     l'envoi : la boîte de Karine reste le canal qui compte. Si la base est
     indisponible, le client n'en sait rien et sa demande est quand même
     arrivée. On ne charge aucune bibliothèque — un fetch suffit, et le site
     public reste sans dépendance.

     La clé utilisée est la clé publique : elle n'autorise que l'insertion.
     Personne ne peut relire les demandes avec, pas même celui qui vient de
     l'envoyer. « return=minimal » évite d'avoir à accorder la lecture. */
  async function consignerDemande(cfg, donnees) {
    const base = (cfg && cfg.supabaseUrl) || "";
    const cle = (cfg && cfg.supabaseClePublique) || "";
    if (!base || !cle) return;

    const texte = (nom) => (donnees.get(nom) || "").toString().trim() || null;
    const nombre = (nom) => {
      const v = parseInt(donnees.get(nom), 10);
      return Number.isFinite(v) ? v : null;
    };
    const liste = (nom) => donnees.getAll(nom).map(String).filter(Boolean);

    const demande = {
      nom: texte("Nom") || "Sans nom",
      email: texte("E-mail"),
      telephone: texte("Téléphone"),
      structure: texte("Structure"),
      rappel: !!donnees.get("Accord de rappel"),
      type_evenement: texte("Type d'événement"),
      date_evenement: texte("Date de l'événement"),
      heure_service: texte("Heure de service"),
      convives: nombre("Nombre de convives"),
      commune: texte("Commune"),
      type_lieu: texte("Type de lieu"),
      style_cuisine: texte("Style de cuisine"),
      formule: texte("Formule envisagée"),
      budget: texte("Budget par personne"),
      plats: liste("Plats souhaités"),
      entrees_boissons: liste("Entrées et boissons"),
      supplements: liste("Prestations en supplément"),
      precisions: texte("Précisions"),
    };

    try {
      const r = await fetch(`${base}/rest/v1/demandes`, {
        method: "POST",
        headers: {
          "apikey": cle,
          "Authorization": `Bearer ${cle}`,
          "Content-Type": "application/json",
          "Prefer": "return=minimal",
        },
        body: JSON.stringify(demande),
      });
      if (!r.ok) console.warn("Carnet de commandes : écriture refusée", r.status);
    } catch (e) {
      console.warn("Carnet de commandes injoignable", e);
    }
  }

  function lienMail(donnees) {
    const groupes = new Map();
    for (const [cle, val] of donnees.entries()) {
      if (!String(val).trim()) continue;
      groupes.set(cle, [...(groupes.get(cle) || []), val]);
    }
    const corps = [...groupes]
      .map(([cle, vals]) => `${cle} : ${vals.join(", ")}`)
      .join("\n");
    const objet = `Demande de devis — ${donnees.get("Type d'événement") || "repas"} du ${donnees.get("Date de l'événement") || "?"}`;
    return `mailto:contact@lepaille-en-queue.fr?subject=${encodeURIComponent(objet)}&body=${encodeURIComponent(corps)}`;
  }

  /* ---------- Démarrage ---------- */
  document.addEventListener("DOMContentLoaded", async () => {
    entete();
    replisPhoto();
    apparitions();
    const cfg = await appliquerConfig();
    carte();
    marches();
    avis(cfg);
    devis(cfg);
    infolettre(cfg);
  });
})();
