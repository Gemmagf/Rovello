"""
Servidor Flask v2 amb:
  - Backend PyTorch (preferit) o TensorFlow (fallback).
  - Fusió bayesiana amb prior geo-temporal opcional.
  - Endpoint /predict accepta camps multipart: image, month, lat, lon, alpha, beta.

Variables d'entorn:
  ROVELLO_MODEL_BACKEND  = "torch" | "tf"        (default: "torch" si disponible)
  ROVELLO_MODEL_PATH     = path al checkpoint     (default: ml/models/best/best.pt)
  ROVELLO_PRIOR_PATH     = path al prior          (default: ml/priors/geo_temporal_prior.pkl)
  ROVELLO_DEFAULT_ALPHA  = pes de la imatge        (default: 1.0)
  ROVELLO_DEFAULT_BETA   = pes del prior           (default: 0.5)

Ús:
  python backend/server_v2.py
"""
from __future__ import annotations

import io
import os
import sys
import json
import logging
from pathlib import Path

import numpy as np
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests as http_req
from concurrent.futures import ThreadPoolExecutor, as_completed

# ----------------------------------------------------------------------------
# Logging estructurat
# ----------------------------------------------------------------------------
logging.basicConfig(
    level=os.environ.get("ROVELLO_LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("rovello")

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent

DEFAULT_TORCH_MODEL = PROJECT_ROOT / "ml" / "models" / "best" / "best.pt"
DEFAULT_TF_MODEL = BACKEND_DIR / "models" / "mushroom_model.h5"
DEFAULT_LE = BACKEND_DIR / "models" / "label_encoder.pkl"
DEFAULT_PRIOR = PROJECT_ROOT / "ml" / "priors" / "geo_temporal_prior.pkl"

MODEL_BACKEND = os.environ.get("ROVELLO_MODEL_BACKEND", "torch").lower()
MODEL_PATH = Path(os.environ.get("ROVELLO_MODEL_PATH", DEFAULT_TORCH_MODEL))
PRIOR_PATH = Path(os.environ.get("ROVELLO_PRIOR_PATH", DEFAULT_PRIOR))
DEFAULT_ALPHA = float(os.environ.get("ROVELLO_DEFAULT_ALPHA", "1.0"))
DEFAULT_BETA = float(os.environ.get("ROVELLO_DEFAULT_BETA", "0.5"))

# ----------------------------------------------------------------------------
# Càrrega del model (lazy: detecta backend disponible)
# ----------------------------------------------------------------------------
class TorchInference:
    def __init__(self, ckpt_path: Path):
        import torch
        from torchvision import transforms
        sys.path.insert(0, str(PROJECT_ROOT))
        from ml.scripts.train_helpers import build_model_for_inference  # type: ignore

        self.torch = torch
        self.device = (
            torch.device("mps") if torch.backends.mps.is_available()
            else torch.device("cuda") if torch.cuda.is_available()
            else torch.device("cpu")
        )
        log.info(f"PyTorch device: {self.device}")

        ckpt = torch.load(ckpt_path, map_location=self.device)
        backbone = ckpt["backbone"]
        num_classes = ckpt["num_classes"]
        img_size = ckpt.get("img_size", 224)
        self.model = build_model_for_inference(backbone, num_classes)
        self.model.load_state_dict(ckpt["model"])
        self.model.eval().to(self.device)
        self.img_size = img_size

        # Carrega label_map per mapejar índex -> nom espècie
        lm_path = ckpt_path.parent / "label_map.json"
        if not lm_path.exists():
            raise FileNotFoundError(f"Falta label_map.json a {lm_path}")
        with open(lm_path) as f:
            label_map = json.load(f)
        # invertit: index -> nom (label_map és nom -> index)
        self.idx_to_class = [None] * len(label_map)
        for sp, i in label_map.items():
            self.idx_to_class[i] = sp

        self.transform = transforms.Compose([
            transforms.Resize(int(img_size * 1.14)),
            transforms.CenterCrop(img_size),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])

    def predict_probs(self, pil_img: Image.Image) -> np.ndarray:
        x = self.transform(pil_img).unsqueeze(0).to(self.device)
        with self.torch.no_grad():
            logits = self.model(x)
            probs = self.torch.softmax(logits, dim=1)[0].cpu().numpy()
        return probs


class TFInference:
    """Fallback: utilitza el model EfficientNet .h5 antic."""
    def __init__(self, model_path: Path, le_path: Path):
        import tensorflow as tf  # type: ignore
        import pickle
        sys.path.insert(0, str(BACKEND_DIR))
        from utils.preprocess import preprocess_pil_image  # type: ignore

        self.model = tf.keras.models.load_model(str(model_path), compile=False)
        with open(le_path, "rb") as f:
            le = pickle.load(f)
        self.idx_to_class = list(le.classes_)
        self._preprocess = preprocess_pil_image
        log.info(f"TF model carregat: {len(self.idx_to_class)} classes")

    def predict_probs(self, pil_img: Image.Image) -> np.ndarray:
        inp = self._preprocess(pil_img)
        preds = self.model.predict(inp, verbose=0)
        return preds[0]


def load_inference():
    """Tria backend disponible. Prefereix Torch si MODEL_PATH existeix."""
    if MODEL_BACKEND == "torch" and MODEL_PATH.exists():
        log.info(f"Carregant Torch model: {MODEL_PATH}")
        return TorchInference(MODEL_PATH)
    if DEFAULT_TF_MODEL.exists():
        log.info(f"Carregant TF model (fallback): {DEFAULT_TF_MODEL}")
        return TFInference(DEFAULT_TF_MODEL, DEFAULT_LE)
    raise SystemExit(
        f"No hi ha cap model disponible. Esperava {MODEL_PATH} (torch) o "
        f"{DEFAULT_TF_MODEL} (tf)."
    )


def load_prior():
    if not PRIOR_PATH.exists():
        log.warning(f"Prior geo-temporal no trobat a {PRIOR_PATH} — la fusió estarà desactivada.")
        return None
    sys.path.insert(0, str(PROJECT_ROOT))
    from ml.priors.fusion import GeoTemporalPrior  # type: ignore
    log.info(f"Carregant prior geo-temporal: {PRIOR_PATH}")
    return GeoTemporalPrior.load(PRIOR_PATH)


# ----------------------------------------------------------------------------
# Inicialització lazy — el prior es carrega a l'arrencada (lleuger),
# el model torch es carrega al primer /predict (evita OOM/timeout al free tier)
# ----------------------------------------------------------------------------
import threading as _threading

APP = Flask(__name__)
CORS(APP)

log.info("Inicialitzant servidor Rovello...")
PRIOR = load_prior()
INFER = None
_infer_lock = _threading.Lock()


def _get_infer():
    global INFER
    if INFER is not None:
        return INFER
    with _infer_lock:
        if INFER is None:
            log.info("Carregant model (primer /predict)...")
            INFER = load_inference()
            if PRIOR is not None and INFER.idx_to_class != PRIOR.species_list:
                log.warning("Ordre de classes del model i prior no coincideix.")
        return INFER


# ----------------------------------------------------------------------------
# Endpoints
# ----------------------------------------------------------------------------
@APP.route("/health", methods=["GET"])
def health():
    infer = INFER  # pot ser None si el model no s'ha carregat encara
    return jsonify({
        "status": "ok",
        "backend": "torch" if isinstance(infer, TorchInference) else ("tf" if infer else "pending"),
        "model_loaded": infer is not None,
        "classes": len(infer.idx_to_class) if infer else 0,
        "prior_loaded": PRIOR is not None,
    })


@APP.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image file in request (field 'image')"}), 400

    file = request.files["image"]
    try:
        img = Image.open(file.stream).convert("RGB")
    except Exception as e:
        log.exception("Imatge invàlida")
        return jsonify({"error": "Invalid image", "detail": str(e)}), 400

    # Camps opcionals de context
    def _opt_float(name):
        v = request.form.get(name)
        if v is None or v == "":
            return None
        try:
            return float(v)
        except ValueError:
            return None

    def _opt_int(name):
        v = request.form.get(name)
        if v is None or v == "":
            return None
        try:
            return int(v)
        except ValueError:
            return None

    month = _opt_int("month")
    lat = _opt_float("lat")
    lon = _opt_float("lon")
    alpha = _opt_float("alpha") or DEFAULT_ALPHA
    beta = _opt_float("beta")
    if beta is None:
        beta = DEFAULT_BETA

    try:
        infer = _get_infer()
        image_probs = infer.predict_probs(img)
    except Exception as e:
        log.exception("Error d'inferència")
        return jsonify({"error": "Inference error", "detail": str(e)}), 500

    use_prior = (
        PRIOR is not None
        and month is not None and lat is not None and lon is not None
        and beta > 0
    )

    if use_prior:
        try:
            fused = PRIOR.fuse(image_probs, month=month, lat=lat, lon=lon,
                               alpha=alpha, beta=beta)
            priors = PRIOR.prior_probs(month, lat, lon)
        except Exception as e:
            log.exception("Error en fusió bayesiana, retornant només imatge")
            fused = image_probs
            priors = None
    else:
        fused = image_probs
        priors = None

    k = min(5, len(fused))
    top_idx = np.argsort(-fused)[:k]
    predictions = []
    for i in top_idx:
        item = {
            "class_index": int(i),
            "class_name": infer.idx_to_class[int(i)],
            "prob": float(fused[int(i)]),
            "image_prob": float(image_probs[int(i)]),
        }
        if priors is not None:
            item["prior_prob"] = float(priors[int(i)])
        predictions.append(item)

    response = {
        "predictions": predictions,
        "num_classes": len(infer.idx_to_class),
        "context_used": use_prior,
    }
    if use_prior:
        response["context"] = {
            "month": month, "lat": lat, "lon": lon, "alpha": alpha, "beta": beta
        }
    log.info(
        f"predict: top1={predictions[0]['class_name']} "
        f"prob={predictions[0]['prob']:.3f} context={use_prior}"
    )
    return jsonify(response)


@APP.route("/forecast", methods=["GET", "POST"])
def forecast():
    """Retorna les espècies més probables per ubicació i mes (sense foto).

    Params (JSON o query string): lat, lon, month, k (default 25)
    """
    if PRIOR is None:
        return jsonify({"error": "Prior geo-temporal no disponible al servidor"}), 503

    if request.method == "POST":
        body = request.json or {}
        lat, lon = body.get("lat"), body.get("lon")
        month, k = body.get("month"), body.get("k", 25)
    else:
        lat, lon = request.args.get("lat"), request.args.get("lon")
        month, k = request.args.get("month"), request.args.get("k", 25)

    try:
        lat, lon, month, k = float(lat), float(lon), int(month), int(k)
    except (TypeError, ValueError):
        return jsonify({"error": "lat, lon i month son requerits i han de ser numèrics"}), 400

    k = min(k, 50)

    try:
        priors = PRIOR.prior_probs(month, lat, lon)
    except Exception as e:
        log.exception("Error calculant prior")
        return jsonify({"error": "Error calculant prior", "detail": str(e)}), 500

    top_idx = np.argsort(-priors)[:k]
    results = [
        {"species": PRIOR.species_list[int(i)], "probability": float(priors[int(i)])}
        for i in top_idx
    ]

    log.info(f"forecast: lat={lat:.2f} lon={lon:.2f} month={month} top1={results[0]['species']}")
    return jsonify({
        "forecast": results,
        "month": month, "lat": lat, "lon": lon,
        "total_species": len(PRIOR.species_list),
    })


# Cache en memòria per evitar repetir cridades a iNaturalist
_inat_cache: dict = {}

# ── Classificació de comestibilitat ──────────────────────────────────────────
_EDIBLE = {
    "Boletus edulis","Lactarius deliciosus","Cantharellus cibarius",
    "Macrolepiota procera","Agaricus campestris","Tricholoma terreum",
    "Hydnum repandum","Pleurotus ostreatus","Leccinum scabrum",
    "Armillaria mellea","Craterellus cornucopioides","Calocybe gambosa",
    "Morchella esculenta","Tuber aestivum","Agaricus bisporus",
    "Cantharellus tubaeformis","Hygrophorus marzuolus","Boletus pinophilus",
    "Suillus luteus","Tricholoma portentosum","Boletus reticulatus",
    "Russula virescens","Russula cyanoxantha","Marasmius oreades",
    "Amanita caesarea","Lycoperdon perlatum","Laccaria laccata",
    "Hygrophorus russula","Laetiporus sulphureus","Cerioporus squamosus",
    "Agrocybe praecox","Boletus aereus","Leccinum aurantiacum",
    "Cantharellus pallens","Fistulina hepatica","Leccinum versipelle",
    "Macrolepiota rhacodes","Pleurotus eryngii","Polyporus umbellatus",
    "Sparassis crispa","Suillus granulatus","Morchella elata",
    "Morchella conica","Hericium erinaceus","Grifola frondosa",
}
_TOXIC = {
    "Amanita phalloides","Amanita muscaria","Amanita virosa",
    "Amanita verna","Amanita pantherina","Galerina marginata",
    "Cortinarius rubellus","Cortinarius orellanus","Cortinarius speciosissimus",
    "Inocybe erubescens","Inocybe patouillardii","Omphalotus olearius",
    "Scleroderma citrinum","Entoloma sinuatum","Tricholoma equestre",
    "Tricholoma pardinum","Hypholoma fasciculare","Paxillus involutus",
    "Gyromitra esculenta","Lepiota brunneoincarnata","Lepiota helveola",
    "Clitocybe rivulosa","Cortinarius gentilis",
}
_CAUTION = {
    # Comestibles però risc de confusió o cal preparació especial
    "Amanita rubescens","Amanita fulva","Amanita crocea",
    "Boletus luridus","Boletus erythropus","Gyromitra gigas",
    "Helvella crispa","Disciotis venosa","Sarcosphaera coronaria",
    "Russula emetica","Lactarius torminosus",
}
_INEDIBLE = {
    # Massa durs, petits o sense valor culinari
    "Trametes versicolor","Ganoderma applanatum","Fomes fomentarius",
    "Stereum hirsutum","Exidia glandulosa","Tremella mesenterica",
    "Daldinia concentrica","Xylaria hypoxylon","Xylaria polymorpha",
    "Byssomerulius corium","Kretzschmaria deusta",
}
# Patògens de plantes (rovells, carbons, oïdis, etc.) — per gènere
_PARASITE_GENERA = {
    "Puccinia","Uromyces","Phragmidium","Triphragmium","Gymnosporangium",
    "Melampsora","Phakopsora","Cronartium","Coleosporium","Microbotryum",
    "Ustilago","Sporisorium","Tilletia","Urocystis","Taphrina","Exobasidium",
    "Erysiphe","Blumeria","Podosphaera","Boeremia","Aecidium","Alternaria",
    "Septoria","Fusarium","Peronospora","Plasmopara","Bremia","Phytophthora",
    "Colletotrichum","Venturia","Hesperomyces","Gibberella","Nectria",
    "Hypomyces","Jackrogersella","Kretzschmaria",
}
# Líquens (simbiosi fong + alga/cianobacteri) — per gènere
_LICHEN_GENERA = {
    "Parmotrema","Parmelia","Xanthoria","Evernia","Usnea","Peltigera",
    "Cladonia","Lobaria","Ramalina","Lecanora","Caloplaca","Diploicia",
    "Circinaria","Aspicilia","Physcia","Physconia","Melanelixia",
}

# ── Tips d'identificació per espècie ─────────────────────────────────────────
_TIPS: dict = {
    "Boletus edulis": [
        "Barret bru castany fins a 25 cm, superfície llisa i seca; porus blancs que envelleixen groc-olivaci",
        "Tija robusta amb retícula blanca fina visible a la part superior; la carn MAI blava al tall",
        "Olor dolça de fruits secs, gust suau; creix sota pins, avets i roures de setembre a novembre",
    ],
    "Lactarius deliciosus": [
        "Barret ataronjat-vermellós amb cercles concèntrics visibles; làmines ataronjades i denses",
        "Al tallar la làmina surt làtex ataronjat abundant; deixa taques verdes als 15-20 min",
        "Tija curta i robusta amb fosses ataronjades (escrobiculada); creix SEMPRE sota pins",
    ],
    "Cantharellus cibarius": [
        "Barret groc ou ondulat fins 10 cm; té PLECS ramificats forquillats (no làmines) que baixen per la tija",
        "Olor fruital d'albercoc i carn ferma i blanca; creix en fagedes i rouredes en tardor",
        "Els plecs no es desprenen del barret; evita Omphalotus olearius ☠️ (làmines vertaderes, taronja viu, sobre fusta en tufs)",
    ],
    "Macrolepiota procera": [
        "Barret gran fins 30 cm amb escames brunes sobre fons blanc; pom central bru prominent al centre",
        "Tija amb anell doble mòbil que llisca amunt i avall, i dibuix zebrat bru-blanc; base bulbosa",
        "Carn blanca que no canvia de color al tall, olor agradable; recull només el barret, la tija és massa dura",
    ],
    "Agaricus campestris": [
        "Barret blanc-grisenc fins 10 cm; làmines inicialment ROSES INTENSES que envelleixen bru-negres",
        "Tija amb anell simple i fràgil; carn que enrogeix lleugerament al tall",
        "Creix en PRATS i camps (mai al bosc); evita Agaricus xanthodermus ☠️ que groga al tall i fa olor de tinta",
    ],
    "Hydnum repandum": [
        "Cara inferior amb AGULLONS blancs-crema (no làmines ni porus) — himenòfor eriçonat únic",
        "Barret bru pàl·lid irregular fins 15 cm; carn blanca ferma, sabor lleugerament amarg (s'elimina blanquejant)",
        "Impossible de confondre per l'eriçonat blanc; creix en grups en boscos de caducifolis a la tardor",
    ],
    "Craterellus cornucopioides": [
        "Forma de trompeta negre-grisenca, fins 12 cm; el cos és completament BUIT per dins",
        "Olor intensa de fruita seca molt agradable, persistent en assecar-se; creix en colònies denses",
        "Molt difícil de veure entre les fulles mortes; busca sous roures en tardor humida",
    ],
    "Morchella esculenta": [
        "Barret cónic-ovoide amb fosses i crestes irregulars; talla'l: tija i barret formen peça contínua BUIDA",
        "Olor agradable; creix a la primavera en boscos de freixes, pomers vells i riberes humides",
        "SEMPRE cuinar mínim 30 min — crues contenen àcid helvèl·lic que causa vòmits greus",
    ],
    "Pleurotus ostreatus": [
        "Barret en forma d'ostra gris-blavós fins 25 cm; làmines blanques DECURRENTS (baixen per la tija)",
        "Creix en rosetes superposades sobre troncs de caducifolis (alzina, faia, pollancres); present tot l'any",
        "Tija excèntrica curta sense anell; olor agradable i carn ferma blanca",
    ],
    "Tricholoma terreum": [
        "Barret grisenc amb escames fibroses radials, fins 8 cm; làmines blanques-grises escotades",
        "Olor suau de farina; creix EXCLUSIVAMENT sous pins (simbiosi obligada)",
        "Evita Tricholoma pardinum ☠️ (barret fins 15 cm, olor de farina rancida intensa, làmines blanques molt denses)",
    ],
    "Armillaria mellea": [
        "Barret bru-mel fins 15 cm amb escames fosques al centre; làmines blanques que es taquen de bru",
        "Tija amb ANELL membranós blanc-grogós persistent; creix en tufs a la base de troncs",
        "Rizoformes negres (cordons) visibles als voltants; CALEN 30 min de cocció mínims, mai crues",
    ],
    "Calocybe gambosa": [
        "Barret blanc-crema robust fins 12 cm; làmines blanques molt denses i apretades",
        "OLOR INTENSA de farina fresca — és el signe més característic d'aquesta espècie",
        "Creix a la primavera en anells als prats; evita Entoloma sinuatum ☠️ (olor afruitat, làmines rosades)",
    ],
    "Amanita phalloides": [
        "⚠️ MORTAL: barret verd-olivaci o grisenc; làmines blanques lliures i denses; tija amb anell ambre",
        "⚠️ VOLVA en forma de SAC BLANC a la base — busca-la sempre, pot estar enterrada sota terra",
        "⚠️ 1 sol barret pot matar un adult; sense antídot; els símptomes tarden 6-12h (massa tard)",
    ],
    "Amanita muscaria": [
        "⚠️ Barret vermell viu amb taques blanques (restes del vel); làmines blanques lliures",
        "⚠️ Base bulbosa amb restes de volva en ANELLS BLANCS concèntrics; anell blanc penjant",
        "⚠️ Provoca al·lucinacions, deliris i danys renals; no hi ha antídot específic",
    ],
    "Amanita virosa": [
        "⚠️ MORTAL: completament BLANC — barret, làmines, tija i volva; barret cònic de jove",
        "⚠️ Olor desagradable persistent; volva gran en sac; anell membranós blanc",
        "⚠️ Mai consumir res completament blanc al bosc sense identificació experta — és l'Àngel Destructor",
    ],
    "Galerina marginata": [
        "⚠️ Bolet petit bru-mel fins 4 cm; làmines brunes; anell membranós marró a la tija",
        "⚠️ Creix sobre fusta de coníferes en grups, semblant a l'Armillaria mellea però molt més petit",
        "⚠️ Conté AMATOXINES en la mateixa dosi letal que A. phalloides; mai collir mels petites sobre fusta",
    ],
    "Cortinarius rubellus": [
        "⚠️ Barret cónic-convex bru-rogenc fins 8 cm; làmines bru-ataronjades; restes de cortina fibrosa a la tija",
        "⚠️ Espores brunes-rovellades; creix en boscos d'avet i bedoll",
        "⚠️ Conté ORELLANINA: símptomes apareixen 2-3 SETMANES DESPRÉS, quan el dany renal ja és irreversible",
    ],
    "Omphalotus olearius": [
        "⚠️ Barret taronja-groc intens fins 15 cm; làmines taronja-brillants que FOSFORESCEN de nit",
        "⚠️ Creix SEMPRE en tufs densos (5-30 ex.) al peu d'oliveres i alzines; mai solitari",
        "⚠️ Làmines VERTADERES (no plecs forquillats com el rossinyol); olor fort de fusta podrida",
    ],
    "Inocybe erubescens": [
        "⚠️ Barret cónic-umbonant BLANC que enrogeix progressivament al tacte i en envellir",
        "⚠️ Olor desagradable de terra humida; creix a la primavera en parcs amb til·lers i teixos",
        "⚠️ Conté MUSCARINA en alta concentració; el blanc que enrogeix al tacte és el signe clau",
    ],
    "Hypholoma fasciculare": [
        "⚠️ Barret groc-sofre fins 7 cm; làmines groguenques-olivàcies; creix en tufs densos sobre fusta",
        "⚠️ SABOR EXTREMADAMENT AMARG (basta tocar la llengua per notar-ho immediatament)",
        "⚠️ Evita confondre amb Armillaria mellea: Hypholoma té làmines olivàcies i sabor amarg, no crema cap al peu",
    ],
    "Scleroderma citrinum": [
        "⚠️ Cos rodó-aplanat dur (com una patata), beige-groc amb escames brunes; sense tija diferenciada",
        "⚠️ Interior NEGRE-VIOLACI quan madur — els Lycoperdon comestibles sempre tenen interior blanc uniforme",
        "⚠️ Olor fort i desagradable; creix mig enterrat en sòls arenosos sous pins i roures",
    ],
    "Amanita rubescens": [
        "Barret bru-rosaci amb taques grises-rosa irregulars (restes del vel universal)",
        "Carn blanca que ENROGEIX clarament al tall i a les picades d'insecte — signe definitiu d'espècie",
        "Anell estriat i base bulbosa amb plaques (no sac); cuit és comestible però cru és tòxic",
    ],
    "Russula virescens": [
        "Barret verd-blavós amb pell ESQUERDADA EN PLAQUES (aspecte de mosaic de ceràmica) inconfusible",
        "Làmines blanques-crema, tija robusta blanca, carn ferma sense canviar de color al tall",
        "Gust dolç o lleugerament amarg; les Russules de gust dolç i làmines blanques solen ser comestibles",
    ],
    "Lycoperdon perlatum": [
        "Cos blanc-crema en forma de pera invertida, cobert de granets blancs que s'esborren en fregar",
        "Talla'l en dues meitats: interior COMPLETAMENT BLANC i uniforme = comestible; qualsevol estructura = descarta",
        "En madurar es torna groc-olivaci i l'àpex s'obre alliberant espores; en aquest estat ja no és comestible",
    ],
    "Cerioporus squamosus": [
        "Barret gran fins 60 cm, ocre amb escames brunes concèntriques; porus GRANS ANGULARS blancs a sota",
        "Tija curta excèntrica negra a la base; creix sobre àlbers, freixos i pollancres",
        "Collir JOVE (carn blanca i tendra); madur és dur com fusta i incomestible",
    ],
    "Laetiporus sulphureus": [
        "Polípor en rosetes superposades GROC-SOFRE intens, fins 40 cm; porus petits grocs a sota",
        "Creix a la base de roures, cirerers i coníferes; carn blanca ferma i suculenta quan és jove",
        "Jove (brillant i flexible) és excel·lent cuinat; madur (apagat i tou) és amarg i indigest",
    ],
    "Agrocybe praecox": [
        "Barret bru-crema fins 7 cm; làmines BRU-CIRERA fosques quan madures (espores brunes)",
        "Olor farinososa característica; creix a la primavera en prats, vores de camí i jardins",
        "Anell membranós fràgil que desapareix aviat; les làmines brunes d'espores el diferencien d'altres",
    ],
    "Disciotis venosa": [
        "Copa gran en forma de disc bru-ocre fins 20 cm; cara superior amb VENES I NERVATURES prominents",
        "Cara exterior pàl·lida i granulosa; creix a la primavera en boscos de ribera i fagedes",
        "⚠️ Olor de lleixiu en fregar; calen 30 min de cocció per eliminar àcid helvèl·lic; MAI crua",
    ],
    "Strobilurus tenacellus": [
        "Bolet petit bru fins 2 cm; creix EXCLUSIVAMENT sobre PINYES enterrades o semisepultes de pi",
        "Tija molt llarga i prima, cartilaginosa i dura (es doblega sense trencar-se); fixa sobre la pinya",
        "La inserció sobre pinya + tija dura que no es trenca el fan inconfusible; massa petit per cuinar",
    ],
    "Sarcosphaera coronaria": [
        "⚠️ Copa gran fins 15 cm que es trenca en estrella irregular exposant l'interior LILA-VIOLETA intens",
        "Creix mig enterrada en boscos de pi negre de muntanya a principis de primavera, sovint amb neu propera",
        "⚠️ Crua és tòxica; cuit pot causar reaccions en algunes persones — millor evitar",
    ],
    "Boletus pinophilus": [
        "Barret bru-vermellós fosc fins 25 cm; porus blancs-crema que envelleixen grocs-verdosos",
        "Tija ventruda bru amb retícula fina a la part superior; la carn MAI blava al tall",
        "Creix EXCLUSIVAMENT sous pins; olor i gust excel·lents, equivalent al cep",
    ],
    "Suillus luteus": [
        "Barret xocolata MOLT VISCÓS quan humit, fins 10 cm; porus petits grocs sota el barret",
        "ANELL membranós prominent i persistent que queda penjat a la tija; tija amb puntets foscos sobre l'anell",
        "Sempre sous pins de dues fulles; retira la pell viscosa abans de cuinar (pot causar irritació digestiva)",
    ],
    "Leccinum scabrum": [
        "Barret bru-grisós fins 15 cm; porus blancs petits; tija robusta amb ESCAMES NEGRES inconfusibles",
        "Carn blanca que vira lentament a gris-rosa al tall (no blau); creix SEMPRE sous bedolls",
        "Les escames negres de la tija (com un dau de pebre) el fan molt reconeixible",
    ],
    "Hygrophorus marzuolus": [
        "Barret gris fins 12 cm, convex i còncau; làmines blanques-grises GRUIXUDES i espaiades",
        "Creix molt aviat a la primavera, fins i tot AMB NEU; exclusivament sous avet o pi negre de muntanya",
        "Tija gris-blanca, olor suau; un dels primers bolets de la temporada primaveral de muntanya",
    ],
    "Gymnosporangium clavariiforme": [
        "🌱 Paràsit amb hospedadors alternants: forma GELATINES ATARONJADES sobre branques de ginebró a la primavera",
        "🌱 A l'estiu parasita fulles de pomeres i pereres, formant taques grogues-ataronjades amb aecidis",
        "🌱 La gelatina ataronjada sobre ginebró (Juniperus) és molt vistosa però no és un bolet comestible",
    ],
    "Triphragmium ulmariae": [
        "🌱 Paràsit de la reina dels prats (Filipendula ulmaria); forma pústules brunes-ataronjades a la cara inferior de les fulles",
        "🌱 No forma carpòfor macroscòpic; s'identifica per les pústules sobre Filipendula en llocs humits",
        "🌱 Sense interès comestible; les espores trifragmíades (3 compartiments) requereixen microscòpia",
    ],
    "Microbotryum pustulatum": [
        "🌱 Carbó de plantes: afecta Silene i altres Caryophyllaceae transformant estams en masses d'espores negres",
        "🌱 No forma bolet; la infecció es veu en les flors de la planta afectada ennegrides",
        "🌱 Sense interès comestible; planta hoste + coloració negra de les parts reproductores = diagnosi",
    ],
    "Kretzschmaria deusta": [
        "Fong en forma de CROSTA NEGRA DURA sobre soques, amb vora blanca-grisenca quan creix activament",
        "De jove és blanc-grisenc i tou; s'endureix i ennegreix amb l'edat",
        "Paràsit intern de caducifolis que causa podridura blanca del cor; no comestible",
    ],
    "Cerioporus squamosus": [
        "Barret gran fins 60 cm, ocre amb escames brunes concèntriques; porus GRANS ANGULARS blancs a sota",
        "Tija curta excèntrica negra a la base; creix sobre àlbers, freixos i pollancres vius o morts",
        "Collir JOVE (carn blanca i tendra); madur és dur com fusta",
    ],
}

# Tips genèrics per gènere (fallback quan l'espècie no és al diccionari)
_GENUS_TIPS: dict = {
    "Amanita": [
        "⚠️ Comprova SEMPRE la VOLVA (sac) a la base — enterrada o no; és el signe més perillós del gènere",
        "Observa si hi ha anell a la tija i si les làmines són LLIURES (no arriben a tocar la tija)",
        "⚠️ Mai consumir cap Amanita sense confirmació experta — el gènere inclou les espècies més letals del món",
    ],
    "Boletus": [
        "Comprova si la carn o els porus blaven o enrogeixen al tall — signal de perill en moltes espècies",
        "Observa el color dels porus (sota): blanc/crema = generalment segur; vermell/taronja = prudència",
        "L'absència de làmines (porus esponjosos en comptes) és característic del grup Boletaceae",
    ],
    "Russula": [
        "Les làmines blanques-crema es trenquen fàcilment (molt fràgils); tija curta i robusta",
        "Tasta un trosset molt petit de làmina: si és MUY PICANT o molt amarg, descarta l'espècie",
        "Pela la cutícula: si es pela fàcilment i uniformement és un senyal; gust dolç = generalment bo",
    ],
    "Lactarius": [
        "Talla el barret o la làmina: el LÀTEX (líquid lletós) que surt és el signe definitiu del gènere",
        "Comprova el COLOR del làtex (blanc, groc, ataronjat, incolor) i si canvia a l'aire",
        "Les làmines son decurrents; l'arbre hoste és clau per identificar l'espècie",
    ],
    "Cortinarius": [
        "⚠️ Gènere molt gran amb espècies MORTALS per orellanina (sense antídot); espores brunes-rovellades",
        "Observa les RESTES DE CORTINA FIBROSA (vel araniforme) a la tija — el signe del gènere",
        "⚠️ Símptomes d'orellanina apareixen 2-3 SETMANES DESPRÉS; mai consumir cap Cortinarius",
    ],
    "Inocybe": [
        "⚠️ Gènere amb moltes espècies TÒXIQUES (muscarina); barret fibril·lós radial, làmines brunes",
        "Olor de farina rancida, terra humida o esperma; espores brunes verrucoses",
        "⚠️ Molt difícils d'identificar entre sí fins amb microscopi; millor no consumir cap Inocybe",
    ],
    "Tricholoma": [
        "Làmines ESCOTADES a la inserció amb la tija; la majoria blanques, grises o grogues",
        "L'arbre hoste és estricte (sous pins o sous caducifolis, no barrejat); comprova-ho sempre",
        "Algunes espècies molt tòxiques (T. pardinum, T. equestre); identificació d'espècie és imprescindible",
    ],
    "Pleurotus": [
        "Creixement lateral sobre FUSTA (tija excèntrica o absent); làmines decurrents (baixen per la tija)",
        "Barret en forma d'ostra o ventall; olor agradable i carn ferma blanca",
        "Confirma que creix sobre fusta (no sobre terra); les espècies del gènere son generalment comestibles",
    ],
    "Galerina": [
        "⚠️ Gènere amb espècies LETALS per amatoxines (mateixa toxina que A. phalloides)",
        "Espores brunes (pols rovellada visible); anell membranós bru fràgil a la part superior de la tija",
        "⚠️ Mai collir bolets petits bruns sobre fusta sense identificació experta completa",
    ],
    "Puccinia": [
        "🌱 Fong PARÀSIT DE PLANTES (rovell); forma pústules taronja, brunes o negres en fulles",
        "🌱 No és un bolet macroscòpic — esporula en superfícies de plantes hoste específiques",
        "🌱 Sense interès culinari; s'identifica per la planta hoste i el tipus de pústules",
    ],
    "Taphrina": [
        "🌱 Paràsit que causa DEFORMACIONS en fulles i fruits (butxaques del préssec, crispadura)",
        "🌱 No forma carpòfor; la infecció es manifesta com inflaments o deformacions en la planta hoste",
        "🌱 Sense interès comestible; s'identifica per la planta hoste i el tipus de deformació",
    ],
    "Erysiphe": [
        "🌱 Fong de l'OÏDI (powdery mildew): forma capa blanca pulverulenta sobre fulles i tiges",
        "🌱 No forma bolet; es veu com una pols blanca en la superfície vegetal",
        "🌱 Sense interès culinari; cada espècie d'Erysiphe és específica d'un hoste vegetal",
    ],
    "Gymnosporangium": [
        "🌱 Paràsit amb HOSPEDADORS ALTERNANTS: Juniperus (ginebró) + Rosaceae (pomeres, espinall)",
        "🌱 En ginebró forma galles ataronjades gelatinoses a la primavera; en Rosaceae taques foliars",
        "🌱 La gelatina ataronjada sobre ginebró és molt vistosa però no és cap bolet comestible",
    ],
    "Microbotryum": [
        "🌱 Carbó de plantes: transforma parts reproductores en masses d'espores NEGRES",
        "🌱 No forma carpòfor; la infecció es manifesta en flors o llavors ennegrides",
        "🌱 Sense interès comestible; s'identifica per la planta hoste afectada",
    ],
    "Parmotrema": [
        "🪨 Liquen foliaceu gran, gris-verd a la cara superior, BLANC a la inferior",
        "🪨 Creix sobre roques i escorces; indica aire NET (molt sensible a la contaminació per SO₂)",
        "🪨 No és un bolet sinó una simbiosi fong + alga; sense interès culinari",
    ],
    "Circinaria": [
        "🪨 Liquen CRUSTACI que creix enganxat a roques calcàries; forma rosetes grises-brunes",
        "🪨 Molt difícil de separar del substrat; indica llarg temps d'estabilitat del medi",
        "🪨 No és un bolet; identificació precisa requereix microscòpia i tests químics",
    ],
    "Usnea": [
        "🪨 Liquen fruticulós PENJANT gris-verdós sobre branques; el signe clau: un FIL ELÀSTIC central visible en estirar-lo",
        "🪨 Indicador excel·lent de qualitat de l'aire; la seva presència confirma poca contaminació",
        "🪨 Medicinal (àcid usníc antibacterià) però no comestible",
    ],
}


def _get_edibility(species_name: str) -> str:
    """Retorna la categoria de comestibilitat per una espècie."""
    if species_name in _EDIBLE:
        return "edible"
    if species_name in _TOXIC:
        return "toxic"
    if species_name in _CAUTION:
        return "caution"
    if species_name in _INEDIBLE:
        return "inedible"
    genus = species_name.split()[0]
    if genus in _PARASITE_GENERA:
        return "parasite"
    if genus in _LICHEN_GENERA:
        return "lichen"
    # Gèneres amb espècies molt tòxiques → precaució per defecte
    if genus in ("Amanita", "Cortinarius", "Inocybe", "Galerina", "Lepiota", "Entoloma"):
        return "caution"
    return "unknown"


def _get_tips(species_name: str) -> list:
    """Retorna els tips d'identificació per una espècie (específics o per gènere)."""
    if species_name in _TIPS:
        return _TIPS[species_name]
    genus = species_name.split()[0]
    if genus in _GENUS_TIPS:
        return _GENUS_TIPS[genus]
    return []


def _fetch_one(species_name: str) -> dict:
    if species_name in _inat_cache:
        return _inat_cache[species_name]
    try:
        r = http_req.get(
            "https://api.inaturalist.org/v1/taxa/autocomplete",
            params={"q": species_name, "per_page": 1, "rank": "species"},
            timeout=6,
        )
        results = r.json().get("results", [])
        if not results:
            info = {}
        else:
            t = results[0]
            photo = t.get("default_photo") or {}
            info = {
                "taxon_id": t.get("id"),
                "common_name": t.get("preferred_common_name", ""),
                "photo_url": photo.get("square_url", ""),
            }
    except Exception:
        info = {}

    info["edibility"] = _get_edibility(species_name)
    info["tips"] = _get_tips(species_name)
    _inat_cache[species_name] = info
    return info


@APP.route("/species-info", methods=["POST"])
def species_info():
    """Retorna foto i nom comú per una llista d'espècies (via iNaturalist)."""
    species_list = (request.json or {}).get("species", [])[:25]
    results = {}
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(_fetch_one, sp): sp for sp in species_list}
        for fut in as_completed(futures):
            sp = futures[fut]
            results[sp] = fut.result()
    return jsonify(results)


@APP.route("/species", methods=["GET"])
def species():
    """Llista de totes les espècies que el model pot predir."""
    return jsonify({"species": INFER.idx_to_class})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    APP.run(host="0.0.0.0", port=port, debug=False)
# gunicorn compatibility alias
app = APP
