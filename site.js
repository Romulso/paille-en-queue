/* =========================================================
   Le Paille en Queue — comportements du site
   Aucune dépendance : le site fonctionne en ouvrant les fichiers
   tels quels. Le contenu vit dans data/*.json.
   ========================================================= */
(() => {
  "use strict";

  const $ = (sel, racine = document) => racine.querySelector(sel);
  const $$ = (sel, racine = document) => [...racine.querySelectorAll(sel)];

  const euros = (n) => `${n} €`;
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
    const ici = location.pathname.split("/").pop() || "index.html";
    $$(".nav a, .menu-mobile a").forEach((a) => {
      if (a.getAttribute("href") === ici) a.setAttribute("aria-current", "page");
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
    $$(".photo img", racine).forEach((img) => {
      const cadre = img.closest(".photo");
      const secours = () => {
        if (cadre.classList.contains("photo-vide")) return;
        const nom = cadre.dataset.nom || img.alt || "";
        let somme = 0;
        for (const c of nom) somme += c.charCodeAt(0);
        cadre.classList.add("photo-vide", `t${(somme % 6) + 1}`);
      };
      img.addEventListener("error", secours);
      if (img.complete && img.naturalWidth === 0) secours();
    });
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
          <img src="images/${echapper(p.slug)}.jpg" alt="${echapper(p.nom)}" loading="lazy" width="600" height="450">
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

    // Les mentions commerciales sont écrites en dur dans le HTML (lisibles
    // sans JavaScript) et rafraîchies ici si data/carte.json a changé.
    const mentions = {
      "data-mention-part": d.mentionPart,
      "data-mention-minimum": d.mentionMinimum,
      "data-mention-non-compris": d.mentionNonCompris,
      "data-mention-livraison": d.mentionLivraison,
      "data-mention-delai": d.mentionDelai,
    };
    Object.entries(mentions).forEach(([attr, texte]) => {
      if (texte) $$(`[${attr}]`).forEach((el) => { el.textContent = texte; });
    });

    replisPhoto();
    apparitions();
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

  async function marches() {
    const zone = $("#zone-marches");
    if (!zone) return;
    const d = await charger("marches");
    const liste = d && Array.isArray(d.marches) ? d.marches : [];

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
            <span class="marche-type ${m.type === "nocturne" ? "nocturne" : ""}">
              ${m.type === "nocturne" ? "Marché nocturne" : "Marché du matin"}
            </span>
          </div>
        </article>`;
    }).join("");
    apparitions();
  }

  /* ---------- Avis ---------- */
  async function avis() {
    const section = $("#section-avis");
    if (!section) return;
    const d = await charger("avis");
    const liste = d && Array.isArray(d.avis) ? d.avis : [];
    if (!liste.length) { section.hidden = true; return; }

    $("#zone-avis").innerHTML = liste.map((a) => `
      <article class="avis apparait">
        ${a.note ? `<div class="etoiles" aria-label="${a.note} sur 5">${"★".repeat(a.note)}${"☆".repeat(5 - a.note)}</div>` : ""}
        <p>« ${echapper(a.texte)} »</p>
        <footer><b>${echapper(a.auteur)}</b>${a.contexte ? echapper(a.contexte) : ""}</footer>
      </article>`).join("");
    section.hidden = false;
    apparitions();
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
    return `mailto:Lepailleenqueue33@gmail.com?subject=${encodeURIComponent(objet)}&body=${encodeURIComponent(corps)}`;
  }

  /* ---------- Démarrage ---------- */
  document.addEventListener("DOMContentLoaded", async () => {
    entete();
    replisPhoto();
    apparitions();
    const cfg = await appliquerConfig();
    carte();
    marches();
    avis();
    devis(cfg);
  });
})();
