const API_URL = process.env.REACT_APP_API_URL || "https://rovello-backend.onrender.com";

const EDIBLE_SPECIES = [
  "Lactarius deliciosus",
  "Boletus edulis",
  "Cantharellus cibarius",
];

const MAX_SIDE = 1024;          // el model treballa a 224 px: 1024 és de sobres
const RETRY_TOTAL_MS = 150000;
// Llindars sobre la probabilitat calibrada (vegeu l'anàlisi de calibratge)
const CONF_SURE = 0.7;   // amb T=0.75, ≥0.7 encerta ~75-95 % en distribució
const CONF_LIKELY = 0.4; // 0.4-0.7 encerta ~40-55 %: «probable», amb avís  // el servidor gratuït pot trigar 1-2 min a despertar-se

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/**
 * Prepara la foto al navegador abans de pujar-la: retalla la regió que l'usuari
 * ha enquadrat (des de la foto ORIGINAL a resolució completa, aplicant
 * l'orientació EXIF) i la redueix a MAX_SIDE. Un bolet petit dins d'una foto de
 * 12 MP arriba així al model com un primer pla nítid.
 * Si alguna cosa falla, retorna el fitxer original (el servidor també la redueix).
 */
export const downscaleImage = async (file, crop = null) => {
  if (!file || !file.type || !file.type.startsWith("image/")) return file;
  if (typeof document === "undefined" || typeof URL === "undefined") return file;
  const url = URL.createObjectURL(file);
  try {
    const img = await new Promise((resolve, reject) => {
      const el = new Image();
      el.onload = () => resolve(el);
      el.onerror = () => reject(new Error("No es pot llegir la imatge"));
      el.src = url;
    });
    const w0 = img.naturalWidth, h0 = img.naturalHeight;
    if (!w0 || !h0) return file;

    // Regió d'origen: el retall triat per l'usuari (normalitzat) o la imatge sencera
    let sx = 0, sy = 0, sw = w0, sh = h0;
    const hasCrop = crop && crop.w > 0 && crop.h > 0 && (crop.w < 0.999 || crop.h < 0.999);
    if (hasCrop) {
      sx = Math.max(0, Math.round(crop.x * w0));
      sy = Math.max(0, Math.round(crop.y * h0));
      sw = Math.min(w0 - sx, Math.round(crop.w * w0));
      sh = Math.min(h0 - sy, Math.round(crop.h * h0));
    }
    const scale = Math.min(1, MAX_SIDE / Math.max(sw, sh));
    if (!hasCrop && scale === 1 && file.type === "image/jpeg" && file.size < 1.5e6) return file;
    const w = Math.max(1, Math.round(sw * scale));
    const h = Math.max(1, Math.round(sh * scale));
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    canvas.getContext("2d").drawImage(img, sx, sy, sw, sh, 0, 0, w, h);
    const blob = await new Promise((r) => canvas.toBlob(r, "image/jpeg", 0.92));
    return blob ? new File([blob], "photo.jpg", { type: "image/jpeg" }) : file;
  } catch {
    return file;
  } finally {
    URL.revokeObjectURL(url);
  }
};

/**
 * Envia la imatge al backend amb context opcional (mes i geolocalització)
 * per millorar la predicció amb fusió bayesiana.
 *
 * @param {File} imageFile - imatge del bolet
 * @param {Object} [context] - context opcional
 * @param {number} [context.month] - mes 1..12 (per defecte: mes actual)
 * @param {number} [context.lat] - latitud
 * @param {number} [context.lon] - longitud
 * @param {number} [context.alpha] - pes de la imatge (default 1.0)
 * @param {number} [context.beta] - pes del prior (default 0.5)
 * @param {Function} [context.onStatus] - callback amb text d'estat per a la UI
 */
export const analyzeMushroom = async (input, context = {}) => {
  const onStatus = typeof context.onStatus === "function" ? context.onStatus : () => {};
  // Accepta un File o una llista [{ file, crop }] (diverses fotos del mateix bolet)
  const photos = Array.isArray(input) ? input : [{ file: input, crop: context.crop || null }];

  onStatus("Preparant la foto...");
  const formData = new FormData();
  for (let i = 0; i < photos.length; i += 1) {
    const upload = await downscaleImage(photos[i].file, photos[i].crop);
    formData.append("image", upload, `photo${i + 1}.jpg`);
  }
  // L'usuari ha enquadrat (zoom) totes les fotos? Si no, el servidor pot provar un zoom central
  const framed = photos.every((p) => p.crop && p.crop.zoom && p.crop.zoom > 1.05);
  formData.append("cropped", framed ? "1" : "0");

  const month = context.month ?? new Date().getMonth() + 1;
  formData.append("month", String(month));

  if (context.lat != null) formData.append("lat", String(context.lat));
  if (context.lon != null) formData.append("lon", String(context.lon));
  if (context.alpha != null) formData.append("alpha", String(context.alpha));
  if (context.beta != null) formData.append("beta", String(context.beta));

  try {
    const started = Date.now();
    let response;
    for (;;) {
      onStatus("Analitzant el teu bolet...");
      response = await fetch(`${API_URL}/predict`, { method: "POST", body: formData });
      if (response.status !== 503 || Date.now() - started > RETRY_TOTAL_MS) break;
      // 503 = el servidor gratuït encara es desperta / carrega el model: esperem i reintentem
      let detail = "";
      try {
        detail = (await response.json()).detail || "";
      } catch {}
      const retryAfter = parseInt(response.headers.get("Retry-After") || "10", 10);
      onStatus(detail ? `Preparant identificador... (${detail})` : "Preparant identificador...");
      await sleep(Math.min(Math.max(retryAfter || 10, 3), 15) * 1000);
    }

    if (!response.ok) {
      // Mostra el motiu real que retorna el backend (p. ex. model carregant-se)
      let detail = "";
      try {
        const err = await response.json();
        detail = err.detail || err.error || "";
      } catch {}
      throw new Error(detail || `Error del servidor (${response.status})`);
    }

    const data = await response.json();
    const predictions = data.predictions || [];
    const top = predictions[0];

    if (!top) {
      throw new Error("No s'han rebut prediccions del model");
    }

    // Fitxa dels 5 candidats (nom comú, foto iNaturalist, comestibilitat curada i
    // consells) — opcional: si falla, la identificació es mostra igualment.
    const infos = await fetchSpeciesInfo(predictions.slice(0, 5).map((p) => p.class_name), context.lang);
    const info = infos[top.class_name] || {};
    const edibilityOf = (name) => infos[name]?.edibility
      || (EDIBLE_SPECIES.includes(name) ? "edible" : "unknown");
    const candidates = predictions.slice(0, 5).map((p) => ({
      name: p.class_name,
      prob: p.prob,
      commonName: infos[p.class_name]?.common_name || "",
      photoUrl: infos[p.class_name]?.photo_url || "",
      edibility: edibilityOf(p.class_name),
    }));
    // Nivell de certesa (probabilitats calibrades al servidor)
    const second = predictions[1]?.prob ?? 0;
    let level = top.prob >= CONF_SURE && top.prob - second >= 0.15 ? "sure"
      : top.prob >= CONF_LIKELY ? "likely" : "unsure";
    // Si el servidor ha hagut d'ampliar el centre de la foto, mai «segur»
    const zoomFallback = data.zoom_fallback === true;
    if (zoomFallback && level === "sure") level = "likely";
    const genus = (data.genera || [])[0] || null;

    return {
      ok: true,
      name: top.class_name,                 // nom científic
      commonName: info.common_name || "",
      photoUrl: info.photo_url || "",
      confidence: top.prob,
      imageProb: top.image_prob,
      priorProb: top.prior_prob,
      edibility: edibilityOf(top.class_name),
      edible: edibilityOf(top.class_name) === "edible",
      tips: Array.isArray(info.tips) ? info.tips : [],
      level,
      uncertain: level !== "sure",
      candidates,
      alternatives: candidates.slice(1, 4),
      genus: genus && genus.n_species > 1 ? genus : null,
      anyToxic: candidates.some((c) => c.edibility === "toxic" || c.edibility === "caution"),
      numPhotos: data.num_photos || photos.length,
      zoomFallback,
      contextUsed: data.context_used === true,
    };
  } catch (error) {
    console.error("Error analitzant el bolet:", error);
    return { ok: false, error: error.message || String(error) };
  }
};

/** Demana al backend la fitxa (nom comú, foto, comestibilitat, consells) d'unes espècies. */
const fetchSpeciesInfo = async (species, lang = "ca") => {
  if (!species.length) return {};
  try {
    const opts = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ species, lang }),
    };
    if (typeof AbortSignal !== "undefined" && AbortSignal.timeout) opts.signal = AbortSignal.timeout(8000);
    const r = await fetch(`${API_URL}/species-info`, opts);
    return r.ok ? await r.json() : {};
  } catch {
    return {};
  }
};

/**
 * Demana la geolocalització del navegador. Retorna {lat, lon} o null si denegat/error.
 */
// Fallback via IP quan la geo del browser falla (error 2 = position unavailable)
const geoByIP = async () => {
  try {
    const r = await fetch('https://ipapi.co/json/', { signal: AbortSignal.timeout(5000) });
    const d = await r.json();
    if (d.latitude && d.longitude)
      return { lat: d.latitude, lon: d.longitude, byIP: true };
  } catch {}
  try {
    const r = await fetch('https://ip-api.com/json/?fields=lat,lon,status', { signal: AbortSignal.timeout(5000) });
    const d = await r.json();
    if (d.status === 'success')
      return { lat: d.lat, lon: d.lon, byIP: true };
  } catch {}
  return null;
};

export const requestGeolocation = (timeoutMs = 8000) =>
  new Promise((resolve) => {
    if (!("geolocation" in navigator)) {
      geoByIP().then(resolve);
      return;
    }
    let done = false;
    const finish = (val) => { if (!done) { done = true; resolve(val); } };
    setTimeout(() => finish(null), timeoutMs);
    navigator.geolocation.getCurrentPosition(
      (pos) => finish({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
      async (err) => {
        // Error 2 (unavailable) o 3 (timeout) → prova per IP
        if (err.code === 2 || err.code === 3) {
          const ipLoc = await geoByIP();
          finish(ipLoc);
        } else {
          finish(null); // Error 1 = denegat → no intentem per IP
        }
      },
      { enableHighAccuracy: false, maximumAge: 60000, timeout: timeoutMs }
    );
  });
