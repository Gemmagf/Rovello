const API_URL = process.env.REACT_APP_API_URL || "https://rovello.onrender.com";

const EDIBLE_SPECIES = [
  "Lactarius deliciosus",
  "Boletus edulis",
  "Cantharellus cibarius",
];

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
 */
export const analyzeMushroom = async (imageFile, context = {}) => {
  const formData = new FormData();
  formData.append("image", imageFile);

  const month = context.month ?? new Date().getMonth() + 1;
  formData.append("month", String(month));

  if (context.lat != null) formData.append("lat", String(context.lat));
  if (context.lon != null) formData.append("lon", String(context.lon));
  if (context.alpha != null) formData.append("alpha", String(context.alpha));
  if (context.beta != null) formData.append("beta", String(context.beta));

  try {
    const response = await fetch(`${API_URL}/predict`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Error en la resposta del servidor");
    }

    const data = await response.json();
    const predictions = data.predictions || [];
    const top = predictions[0];

    if (!top) {
      throw new Error("No s'han rebut prediccions del model");
    }

    const isEdible = EDIBLE_SPECIES.includes(top.class_name);

    return {
      name: top.class_name,
      description: `Confiança ${(top.prob * 100).toFixed(1)}%`,
      edible: isEdible,
      toxicity: isEdible ? "Cap risc" : "Alt risc",
      tips: isEdible
        ? "Aquest bolet és comestible i apreciat. Tot i així, assegura't que no hi hagi confusions amb espècies similars."
        : "Evita consumir-lo. Podria confondre's amb bolets tòxics similars.",
      // Camps addicionals per UI avançada
      alternatives: predictions.slice(1, 4).map((p) => ({
        name: p.class_name,
        prob: p.prob,
      })),
      contextUsed: data.context_used === true,
      imageProb: top.image_prob,
      priorProb: top.prior_prob,
    };
  } catch (error) {
    console.error("Error analitzant el bolet:", error);
    return {
      name: "Error en la detecció",
      description: "Alguna cosa ha anat malament. Prova amb una altra foto més clara.",
      edible: false,
      toxicity: "Desconegut",
      tips: "Assegura't que la foto sigui nítida i ben il·luminada.",
    };
  }
};

/**
 * Demana la geolocalització del navegador. Retorna {lat, lon} o null si denegat/error.
 */
export const requestGeolocation = (timeoutMs = 8000) =>
  new Promise((resolve) => {
    if (!("geolocation" in navigator)) {
      resolve(null);
      return;
    }
    let resolved = false;
    const tid = setTimeout(() => {
      if (!resolved) {
        resolved = true;
        resolve(null);
      }
    }, timeoutMs);

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        if (resolved) return;
        resolved = true;
        clearTimeout(tid);
        resolve({ lat: pos.coords.latitude, lon: pos.coords.longitude });
      },
      () => {
        if (resolved) return;
        resolved = true;
        clearTimeout(tid);
        resolve(null);
      },
      { enableHighAccuracy: false, maximumAge: 60000, timeout: timeoutMs }
    );
  });
