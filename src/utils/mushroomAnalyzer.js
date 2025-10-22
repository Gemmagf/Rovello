export const analyzeMushroom = async (imageFile) => {
  const formData = new FormData();
  formData.append("image", imageFile);

  try {
    const response = await fetch("https://rovello.onrender.com/predict", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Error en la resposta del servidor");
    }

    const data = await response.json();

    // 🔍 Prenem la predicció principal
    const top = data.predictions && data.predictions.length > 0 ? data.predictions[0] : null;

    if (!top) {
      throw new Error("No s'han rebut prediccions del model");
    }

    // 🔎 Exemple simple de classificació comestible/tòxic
    // (pots afinar això més endavant amb una base de dades real)
    const edibleSpecies = ["Lactarius deliciosus", "Boletus edulis", "Cantharellus cibarius"];
    const isEdible = edibleSpecies.includes(top.class_name);

    // 🧠 Format adaptat al que espera ResultDisplay.js
    return {
      name: top.class_name,
      description: `Confiança ${(top.prob * 100).toFixed(1)}%`,
      edible: isEdible,
      toxicity: isEdible ? "Cap risc" : "Alt risc",
      tips: isEdible
        ? "Aquest bolet és comestible i apreciat. Tot i així, assegura’t que no hi hagi confusions amb espècies similars."
        : "Evita consumir-lo. Podria confondre’s amb bolets tòxics similars.",
    };

  } catch (error) {
    console.error("Error analitzant el bolet:", error);
    return {
      name: "Error en la detecció",
      description: "Alguna cosa ha anat malament. Prova amb una altra foto més clara.",
      edible: false,
      toxicity: "Desconegut",
      tips: "Assegura’t que la foto sigui nítida i ben il·luminada.",
    };
  }
};