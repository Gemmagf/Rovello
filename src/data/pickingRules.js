/**
 * Normativa de recol·lecció de bolets per regió.
 *
 * Esquema d'una regla:
 *   closedDays:  [desDeDia, finsADia] de cada mes (inclusius) o null
 *   maxKg:       límit per persona i dia (número) o null
 *   limits:      [{ what: {ca,en,de}, kg }] límits per espècie (opcional)
 *   night:       { from: 'HH:MM', to: 'HH:MM' } o null
 *   reserves:    true → recorda la prohibició a zones protegides
 *   communal:    true → les normes depenen del municipi
 *   notes:       { ca, en, de } text curt (opcional)
 *   source:      URL oficial · updated: data de la font
 *
 * Suïssa: transcripció de la taula oficial de la VAPKO (Associació suïssa
 * d'organismes de control de bolets), «Kantonale und kommunale
 * Pilzsammelbestimmungen», estat 08.02.2026. Catalunya: Generalitat (DARP).
 * SEMPRE es mostra un avís d'informació orientativa a la UI.
 */
export const SOURCES = {
  vapko: 'https://www.vapko.ch/de/oekologie/kantonale-und-kommunale-pilzsammelbestimmungen',
  gencat: 'https://agricultura.gencat.cat/web/.content/06-medi-natural/boscos/gestio-forestal/productes-bosc/bolets/guia-bones-practiques-recolleccio-bolets.pdf',
};

const N = (ca, en, de) => ({ ca, en, de });
const MORELS = N('múrgoles', 'morels', 'Morcheln');
const CHANT = N('rossinyols', 'chanterelles', 'Eierschwämme');
const PORCINI = N('ceps', 'porcini', 'Steinpilze');

const NO_ORG = N(
  'Prohibida la recol·lecció organitzada o comercial.',
  'Organised or commercial collecting is prohibited.',
  'Organisiertes bzw. gewerbliches Sammeln ist verboten.',
);

export const CH = {
  updated: '2026-02',
  general: { closedDays: null, maxKg: null, night: null, reserves: true, source: SOURCES.vapko },
  cantons: {
    'CH-AG': { notes: N('Prohibida la recol·lecció organitzada; cal permís per a la recol·lecció comercial.',
                        'Organised collecting is prohibited; a permit is required for commercial picking.',
                        'Organisiertes Sammeln verboten; gewerbliches Sammeln nur mit Bewilligung.') },
    'CH-AI': { maxKg: 2, notes: N('Només exemplars madurs, collits a mà amb cura.',
                                  'Only mature specimens, carefully picked by hand.',
                                  'Nur ausgewachsene Pilze, sorgfältig von Hand gepflückt.') },
    'CH-AR': { maxKg: 2, notes: N('Només a mà; prohibida la recol·lecció comercial o organitzada.',
                                  'Hand-picking only; commercial or organised collecting prohibited.',
                                  'Nur von Hand; gewerbliches oder organisiertes Sammeln verboten.') },
    'CH-BE': { maxKg: 2, notes: N('Prohibida la recol·lecció organitzada (excepte sortides didàctiques guiades).',
                                  'Organised collecting is banned (except guided educational excursions).',
                                  'Organisiertes Sammeln verboten (ausser geführte Lehrexkursionen).') },
    'CH-BL': {},
    'CH-BS': {},
    'CH-FR': { maxKg: 2, night: { from: '20:00', to: '07:00' },
               notes: N('Prohibida la destrucció deliberada de bolets.', 'Wanton destruction of mushrooms is prohibited.',
                        'Die mutwillige Zerstörung von Pilzen ist verboten.') },
    'CH-GE': { maxKg: 2 },
    'CH-GL': { closedDays: [1, 10], maxKg: 2,
               notes: N('Prohibida la recol·lecció organitzada (excepte societats i escoles).',
                        'Organised collecting prohibited (except clubs and schools).',
                        'Organisiertes Sammeln verboten (ausser Vereine und Schulen).') },
    'CH-GR': { closedDays: [1, 10], maxKg: 2,
               notes: N('Prohibits els grups de més de 3 persones (excepte famílies) i la destrucció de bolets.',
                        'Groups of more than 3 people are banned (families excepted); destroying mushrooms is prohibited.',
                        'Gruppen über 3 Personen verboten (ausser Familien); Zerstörung von Pilzen verboten.') },
    'CH-JU': { maxKg: 2, notes: N('Prohibida la recol·lecció organitzada; només a mà i amb cura.',
                                  'Organised collecting banned; careful hand-picking only.',
                                  'Organisiertes Sammeln verboten; nur sorgfältig von Hand.') },
    'CH-LU': { closedDays: [1, 7], maxKg: 2, limits: [{ what: MORELS, kg: 0.5 }, { what: CHANT, kg: 0.5 }],
               notes: N('Prohibides la recol·lecció organitzada, la recol·lecció indiscriminada i la destrucció de bolets.',
                        'Organised collecting, indiscriminate picking and destruction of mushrooms are prohibited.',
                        'Organisiertes Sammeln, wahlloses Pflücken und Zerstören von Pilzen verboten.') },
    'CH-NE': {},
    'CH-NW': { maxKg: 1, notes: N('Prohibida la recol·lecció organitzada; cal permís per a la comercial.',
                                  'Organised collecting banned; commercial picking requires a permit.',
                                  'Organisiertes Sammeln verboten; gewerbliches nur mit Bewilligung.') },
    'CH-OW': { closedDays: [1, 7], maxKg: 2, limits: [{ what: MORELS, kg: 0.5 }],
               notes: N('També prohibit collir de nit. Prohibida la recol·lecció organitzada o comercial.',
                        'Night collecting is also prohibited. Organised or commercial collecting is banned.',
                        'Zudem Sammelverbot in der Nacht. Organisiertes bzw. gewerbliches Sammeln verboten.') },
    'CH-SG': { communal: true, notes: N('Les normes (dies de veda i quantitats) varien per municipi: consulta l’ajuntament.',
                                        'Rules (closed days and quantities) vary by municipality: check with the commune.',
                                        'Schonzeiten und Mengen sind kommunal geregelt: bei der Gemeinde nachfragen.') },
    'CH-SH': { notes: N('Sense normes especials, excepte Buchberg i Rüdlingen, que segueixen les de Zúric.',
                        'No special rules, except Buchberg and Rüdlingen, which follow the Zurich rules.',
                        'Keine besonderen Bestimmungen; Buchberg und Rüdlingen folgen den Zürcher Regeln.') },
    'CH-SO': {},
    'CH-SZ': { maxKg: 2, limits: [{ what: MORELS, kg: 1 }],
               notes: N('Prohibits els esdeveniments de recol·lecció organitzada (excepcions per a ciència i educació).',
                        'Organised collecting events are prohibited (exceptions for science and education).',
                        'Organisierte Sammelanlässe verboten (Ausnahmen für Wissenschaft und Bildung).') },
    'CH-TG': { maxKg: 1 },
    'CH-TI': { maxKg: 3, night: { from: '20:00', to: '07:00' },
               notes: N('Només a mà; prohibida la destrucció de bolets.', 'Hand-picking only; destroying mushrooms is prohibited.',
                        'Nur von Hand; Zerstörung von Pilzen verboten.') },
    'CH-UR': { maxKg: 3, limits: [{ what: MORELS, kg: 0.5 }, { what: CHANT, kg: 2 }],
               notes: N('Sense eines; múrgoles només a partir de l’1 d’abril. Prohibida la recol·lecció comercial o organitzada.',
                        'No tools; morels only from 1 April. Commercial or organised collecting is banned.',
                        'Keine Hilfsmittel; Morcheln erst ab 1. April. Gewerbliches oder organisiertes Sammeln verboten.') },
    'CH-VD': { maxKg: 2, night: { from: '20:00', to: '07:00' },
               notes: N('Recol·lecció comercial (fins a 6 kg) només amb permís i curs de certificació.',
                        'Commercial harvesting (up to 6 kg) only with a permit and a certification course.',
                        'Gewerbliches Sammeln (bis 6 kg) nur mit Bewilligung und Zertifizierungskurs.') },
    'CH-VS': {},
    'CH-ZG': {},
    'CH-ZH': { closedDays: [1, 10], maxKg: 1,
               notes: N('Només espècies conegudes; prohibida la destrucció de bolets.',
                        'Only species you know; destroying mushrooms is prohibited.',
                        'Nur bekannte Arten; Zerstörung von Pilzen verboten.') },
  },
};

// Liechtenstein (a la mateixa taula de la VAPKO)
export const LI = {
  updated: '2026-02', closedDays: [1, 10], maxKg: 2, night: { from: '20:00', to: '08:00' }, reserves: true,
  limits: [{ what: PORCINI, kg: 1 }, { what: CHANT, kg: 1 }, { what: MORELS, kg: 1 }],
  notes: NO_ORG, source: SOURCES.vapko,
};

// Catalunya: no hi ha normativa micològica general (excepte tòfones); regulació per zones
export const ES_CT = {
  updated: '2026-09',
  closedDays: null, maxKg: null, night: null, reserves: true, source: SOURCES.gencat,
  notes: N(
    'Catalunya no té normativa general de recol·lecció (només per a tòfones), però hi ha zones regulades: al Paratge Natural de Poblet cal autorització, al Parc Nacional d’Aigüestortes és prohibit collir-ne, i hi ha regulacions pròpies en boscos públics de l’Alt Pirineu, els Ports i el Ripollès. Bones pràctiques: cistell (no bosses de plàstic), collir els bolets sencers i tapar el forat, mai rasclets ni remoure el sòl, només espècies conegudes i quantitats de consum, i respectar la propietat privada.',
    'Catalonia has no general picking regulation (only for truffles), but some areas are regulated: a permit is required in the Poblet natural site, picking is forbidden in the Aigüestortes National Park, and public forests in Alt Pirineu, Els Ports and Ripollès have their own rules. Good practice: use a basket (no plastic bags), pick whole mushrooms and cover the hole, never use rakes or disturb the soil, only known species in household quantities, and respect private property.',
    'Katalonien hat keine allgemeine Sammelverordnung (nur für Trüffel), aber regulierte Gebiete: im Naturgebiet Poblet ist eine Bewilligung nötig, im Nationalpark Aigüestortes ist das Sammeln verboten, und öffentliche Wälder in Alt Pirineu, Els Ports und Ripollès haben eigene Regeln. Gute Praxis: Korb statt Plastiktüte, Pilze ganz entnehmen und das Loch zudecken, keine Rechen und Boden nicht aufwühlen, nur bekannte Arten in Haushaltsmengen, Privateigentum respektieren.',
  ),
};

/** Retorna { kind, rules } per a un país/regió (codis ISO 3166-2 de Nominatim). */
export function getRulesFor(country, region) {
  if (country === 'CH') {
    const r = CH.cantons[region];
    if (r) return { kind: 'ch-canton', rules: { ...CH.general, ...r, updated: r.updated || CH.updated } };
    return { kind: 'ch-general', rules: { ...CH.general, updated: CH.updated } };
  }
  if (country === 'LI') return { kind: 'ch-canton', rules: LI };
  if (country === 'ES' && (region === 'ES-CT' || !region)) return { kind: 'es-ct', rules: ES_CT };
  return { kind: null, rules: null };
}
