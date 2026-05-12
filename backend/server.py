# backend/server.py
import io
import os
import sys
import json
import logging
import pickle
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import requests as http_req
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf

from utils.preprocess import preprocess_pil_image

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("rovello")

APP = Flask(__name__)
CORS(APP)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH  = BASE_DIR / "models" / "mushroom_model.h5"
LE_PATH     = BASE_DIR / "models" / "label_encoder.pkl"
PRIOR_PATH  = BASE_DIR / "models" / "geo_temporal_prior.pkl"
FUSION_PATH = BASE_DIR / "fusion.py"

# ── Model TF ─────────────────────────────────────────────────────────────────
log.info("Carregant model TF...")
model = tf.keras.models.load_model(str(MODEL_PATH), compile=False)
with open(LE_PATH, "rb") as f:
    le = pickle.load(f)
NUM_CLASSES = len(le.classes_)
log.info(f"Model carregat: {NUM_CLASSES} classes")

# ── Prior geo-temporal ────────────────────────────────────────────────────────
PRIOR = None
try:
    sys.path.insert(0, str(BASE_DIR))
    from fusion import GeoTemporalPrior  # type: ignore
    PRIOR = GeoTemporalPrior.load(str(PRIOR_PATH))
    log.info(f"Prior carregat: {len(PRIOR.species_list)} espècies")
except Exception as e:
    log.warning(f"Prior no disponible: {e}")

# ── Cache iNaturalist ─────────────────────────────────────────────────────────
_inat_cache: dict = {}

# ── Comestibilitat ────────────────────────────────────────────────────────────
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
    "Amanita rubescens","Amanita fulva","Amanita crocea",
    "Boletus luridus","Boletus erythropus","Gyromitra gigas",
    "Helvella crispa","Disciotis venosa","Sarcosphaera coronaria",
    "Russula emetica","Lactarius torminosus",
}
_INEDIBLE = {
    "Trametes versicolor","Ganoderma applanatum","Fomes fomentarius",
    "Stereum hirsutum","Exidia glandulosa","Tremella mesenterica",
    "Daldinia concentrica","Xylaria hypoxylon","Xylaria polymorpha",
    "Byssomerulius corium","Kretzschmaria deusta",
}
_PARASITE_GENERA = {
    "Puccinia","Uromyces","Phragmidium","Triphragmium","Gymnosporangium",
    "Melampsora","Phakopsora","Cronartium","Coleosporium","Microbotryum",
    "Ustilago","Sporisorium","Tilletia","Urocystis","Taphrina","Exobasidium",
    "Erysiphe","Blumeria","Podosphaera","Boeremia","Aecidium","Alternaria",
    "Septoria","Fusarium","Peronospora","Plasmopara","Bremia","Phytophthora",
    "Colletotrichum","Venturia","Hesperomyces","Gibberella","Nectria",
    "Hypomyces","Jackrogersella","Kretzschmaria",
}
_LICHEN_GENERA = {
    "Parmotrema","Parmelia","Xanthoria","Evernia","Usnea","Peltigera",
    "Cladonia","Lobaria","Ramalina","Lecanora","Caloplaca","Diploicia",
    "Circinaria","Aspicilia","Physcia","Physconia","Melanelixia",
}

# ── Tips per espècie ──────────────────────────────────────────────────────────
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
        "Barret bru pàl·lid irregular fins 15 cm; carn blanca ferma, sabor lleugerament amarg",
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
        "Creix en rosetes superposades sobre troncs de caducifolis; present tot l'any",
        "Tija excèntrica curta sense anell; olor agradable i carn ferma blanca",
    ],
    "Amanita phalloides": [
        "⚠️ MORTAL: barret verd-olivaci o grisenc; làmines blanques lliures i denses; tija amb anell ambre",
        "⚠️ VOLVA en forma de SAC BLANC a la base — busca-la sempre, pot estar enterrada sota terra",
        "⚠️ 1 sol barret pot matar un adult; sense antídot; els símptomes tarden 6-12h",
    ],
    "Amanita muscaria": [
        "⚠️ Barret vermell viu amb taques blanques (restes del vel); làmines blanques lliures",
        "⚠️ Base bulbosa amb restes de volva en ANELLS BLANCS concèntrics; anell blanc penjant",
        "⚠️ Provoca al·lucinacions, deliris i danys renals; no hi ha antídot específic",
    ],
    "Galerina marginata": [
        "⚠️ Bolet petit bru-mel fins 4 cm; làmines brunes; anell membranós marró a la tija",
        "⚠️ Creix sobre fusta de coníferes en grups, semblant a Armillaria però molt més petit",
        "⚠️ Conté AMATOXINES en la mateixa dosi letal que A. phalloides; mai collir mels petites sobre fusta",
    ],
    "Cortinarius rubellus": [
        "⚠️ Barret cónic-convex bru-rogenc fins 8 cm; làmines bru-ataronjades; restes de cortina a la tija",
        "⚠️ Espores brunes-rovellades; creix en boscos d'avet i bedoll",
        "⚠️ Conté ORELLANINA: símptomes apareixen 2-3 SETMANES DESPRÉS, quan el dany renal ja és irreversible",
    ],
    "Omphalotus olearius": [
        "⚠️ Barret taronja-groc intens fins 15 cm; làmines taronja-brillants que FOSFORESCEN de nit",
        "⚠️ Creix SEMPRE en tufs densos al peu d'oliveres i alzines; mai solitari",
        "⚠️ Làmines VERTADERES (no plecs forquillats com el rossinyol); olor fort de fusta podrida",
    ],
    "Hypholoma fasciculare": [
        "⚠️ Barret groc-sofre fins 7 cm; làmines groguenques-olivàcies; creix en tufs densos sobre fusta",
        "⚠️ SABOR EXTREMADAMENT AMARG (basta tocar la llengua per notar-ho immediatament)",
        "⚠️ Evita confondre amb Armillaria mellea: Hypholoma té làmines olivàcies i sabor amarg",
    ],
    "Russula virescens": [
        "Barret verd-blavós amb pell ESQUERDADA EN PLAQUES (aspecte de mosaic de ceràmica) inconfusible",
        "Làmines blanques-crema, tija robusta blanca, carn ferma sense canviar de color al tall",
        "Gust dolç o lleugerament amarg; les Russules de gust dolç i làmines blanques solen ser comestibles",
    ],
    "Lycoperdon perlatum": [
        "Cos blanc-crema en forma de pera invertida, cobert de granets blancs",
        "Talla'l en dues meitats: interior COMPLETAMENT BLANC i uniforme = comestible",
        "En madurar es torna groc-olivaci i l'àpex s'obre alliberant espores; en aquest estat ja no és comestible",
    ],
    "Laetiporus sulphureus": [
        "Polípor en rosetes superposades GROC-SOFRE intens, fins 40 cm; porus petits grocs a sota",
        "Creix a la base de roures, cirerers i coníferes; carn blanca ferma i suculenta quan és jove",
        "Jove (brillant i flexible) és excel·lent cuinat; madur (apagat i tou) és amarg i indigest",
    ],
    "Suillus luteus": [
        "Barret xocolata MOLT VISCÓS quan humit, fins 10 cm; porus petits grocs sota el barret",
        "ANELL membranós prominent i persistent que queda penjat a la tija",
        "Sempre sous pins de dues fulles; retira la pell viscosa abans de cuinar",
    ],
    "Leccinum scabrum": [
        "Barret bru-grisós fins 15 cm; porus blancs petits; tija robusta amb ESCAMES NEGRES inconfusibles",
        "Carn blanca que vira lentament a gris-rosa al tall (no blau); creix SEMPRE sous bedolls",
        "Les escames negres de la tija el fan molt reconeixible",
    ],
    "Armillaria mellea": [
        "Barret bru-mel fins 15 cm amb escames fosques al centre; làmines blanques que es taquen de bru",
        "Tija amb ANELL membranós blanc-grogós persistent; creix en tufs a la base de troncs",
        "CALEN 30 min de cocció mínims, mai crues",
    ],
    "Calocybe gambosa": [
        "Barret blanc-crema robust fins 12 cm; làmines blanques molt denses i apretades",
        "OLOR INTENSA de farina fresca — és el signe més característic d'aquesta espècie",
        "Creix a la primavera en anells als prats; evita Entoloma sinuatum ☠️ (olor afruitat, làmines rosades)",
    ],
}

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
        "Creixement lateral sobre FUSTA (tija excèntrica o absent); làmines decurrents",
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
    "Gymnosporangium": [
        "🌱 Paràsit amb HOSPEDADORS ALTERNANTS: Juniperus (ginebró) + Rosaceae (pomeres, espinall)",
        "🌱 En ginebró forma galles ataronjades gelatinoses a la primavera; en Rosaceae taques foliars",
        "🌱 La gelatina ataronjada sobre ginebró és molt vistosa però no és cap bolet comestible",
    ],
    "Parmotrema": [
        "🪨 Liquen foliaceu gran, gris-verd a la cara superior, BLANC a la inferior",
        "🪨 Creix sobre roques i escorces; indica aire NET (molt sensible a la contaminació)",
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
    if species_name in _EDIBLE:   return "edible"
    if species_name in _TOXIC:    return "toxic"
    if species_name in _CAUTION:  return "caution"
    if species_name in _INEDIBLE: return "inedible"
    genus = species_name.split()[0]
    if genus in _PARASITE_GENERA: return "parasite"
    if genus in _LICHEN_GENERA:   return "lichen"
    if genus in ("Amanita", "Cortinarius", "Inocybe", "Galerina", "Lepiota", "Entoloma"):
        return "caution"
    return "unknown"


def _get_tips(species_name: str) -> list:
    if species_name in _TIPS: return _TIPS[species_name]
    genus = species_name.split()[0]
    return _GENUS_TIPS.get(genus, [])


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


# ── Endpoints ─────────────────────────────────────────────────────────────────

@APP.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "classes": int(NUM_CLASSES),
        "prior_loaded": PRIOR is not None,
        "backend": "tf",
    })


@APP.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image file in request (field 'image')"}), 400
    file = request.files["image"]
    try:
        img = Image.open(file.stream).convert("RGB")
    except Exception as e:
        return jsonify({"error": "Invalid image", "detail": str(e)}), 400
    try:
        inp = preprocess_pil_image(img)
        preds = model.predict(inp, verbose=0)
        probs = preds[0]
        topk = int(min(3, len(probs)))
        top_idx = np.argsort(-probs)[:topk]
        results = [
            {"class_index": int(i), "class_name": str(le.classes_[i]), "prob": float(probs[i])}
            for i in top_idx
        ]
        return jsonify({"predictions": results, "num_classes": NUM_CLASSES})
    except Exception as e:
        return jsonify({"error": "Inference error", "detail": str(e)}), 500


@APP.route("/forecast", methods=["GET", "POST"])
def forecast():
    if PRIOR is None:
        return jsonify({"error": "Prior geo-temporal no disponible al servidor"}), 503
    if request.method == "POST":
        body = request.json or {}
        lat, lon, month, k = body.get("lat"), body.get("lon"), body.get("month"), body.get("k", 25)
    else:
        lat, lon = request.args.get("lat"), request.args.get("lon")
        month, k = request.args.get("month"), request.args.get("k", 25)
    try:
        lat, lon, month, k = float(lat), float(lon), int(month), int(k)
    except (TypeError, ValueError):
        return jsonify({"error": "lat, lon i month son requerits i han de ser numerics"}), 400
    k = min(k, 50)
    try:
        priors = PRIOR.prior_probs(month, lat, lon)
    except Exception as e:
        return jsonify({"error": "Error calculant prior", "detail": str(e)}), 500
    top_idx = np.argsort(-priors)[:k]
    results = [
        {"species": PRIOR.species_list[int(i)], "probability": float(priors[int(i)])}
        for i in top_idx
    ]
    log.info(f"forecast lat={lat:.2f} lon={lon:.2f} month={month} top1={results[0]['species']}")
    return jsonify({
        "forecast": results,
        "month": month, "lat": lat, "lon": lon,
        "total_species": len(PRIOR.species_list),
    })


@APP.route("/species-info", methods=["POST"])
def species_info():
    species_list = (request.json or {}).get("species", [])[:25]
    results = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(_fetch_one, sp): sp for sp in species_list}
        for fut in as_completed(futures):
            sp = futures[fut]
            try:
                results[sp] = fut.result()
            except Exception:
                results[sp] = {"edibility": _get_edibility(sp), "tips": _get_tips(sp)}
    return jsonify(results)


if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=5000, debug=False)
