"""Consells d'identificació traduïts (EN, DE). Les claus i l'ordre coincideixen
amb _TIPS / _GENUS_TIPS de server.py (català, font original). Els prefixos
⚠️ / 🌱 / 🪨 es conserven: el frontend els converteix en icones.
"""

TIPS_I18N = {
  "en": {
    "Boletus edulis": [
      "Chestnut-brown cap up to 25 cm, smooth dry surface; white pores that age yellow-olive",
      "Stout stem with a fine white net (reticulum) visible at the top; flesh NEVER turns blue when cut",
      "Sweet nutty smell, mild taste; grows under pines, firs and oaks from September to November",
    ],
    "Lactarius deliciosus": [
      "Orange-red cap with visible concentric rings; dense orange gills",
      "Cutting the gills releases abundant orange latex; green stains appear after 15-20 min",
      "Short stout stem with orange pits (scrobiculate); ALWAYS grows under pines",
    ],
    "Cantharellus cibarius": [
      "Egg-yellow wavy cap up to 10 cm; it has forked, branching FOLDS (not gills) running down the stem",
      "Fruity apricot smell and firm white flesh; grows in beech and oak woods in autumn",
      "The folds cannot be peeled off the cap; avoid Omphalotus olearius ☠️ (true gills, bright orange, in tufts on wood)",
    ],
    "Macrolepiota procera": [
      "Large cap up to 30 cm with brown scales on a white background; prominent brown central boss",
      "Stem with a double movable ring that slides up and down, and a brown-white snakeskin pattern; bulbous base",
      "White flesh that does not change colour when cut, pleasant smell; take only the cap, the stem is too tough",
    ],
    "Agaricus campestris": [
      "White-greyish cap up to 10 cm; gills initially DEEP PINK, ageing brown-black",
      "Stem with a simple fragile ring; flesh reddens slightly when cut",
      "Grows in MEADOWS and fields (never in woods); avoid Agaricus xanthodermus ☠️ which yellows when cut and smells of ink",
    ],
    "Hydnum repandum": [
      "Underside with white-cream SPINES (no gills or pores) — a unique tooth-like hymenophore",
      "Irregular pale brown cap up to 15 cm; firm white flesh, slightly bitter taste (removed by blanching)",
      "Impossible to confuse thanks to the white spines; grows in groups in deciduous woods in autumn",
    ],
    "Craterellus cornucopioides": [
      "Black-grey trumpet shape, up to 12 cm; the body is completely HOLLOW inside",
      "Intense, very pleasant dried-fruit smell that persists when dried; grows in dense colonies",
      "Very hard to see among dead leaves; look under oaks in a wet autumn",
    ],
    "Morchella esculenta": [
      "Conical-ovoid cap with irregular pits and ridges; cut it: stem and cap form one continuous HOLLOW piece",
      "Pleasant smell; grows in spring in ash woods, old orchards and damp riversides",
      "ALWAYS cook for at least 30 min — raw they contain helvellic acid, which causes severe vomiting",
    ],
    "Pleurotus ostreatus": [
      "Oyster-shaped grey-bluish cap up to 25 cm; white DECURRENT gills (running down the stem)",
      "Grows in overlapping rosettes on deciduous trunks (holm oak, beech, poplar); present all year",
      "Short off-centre stem without a ring; pleasant smell and firm white flesh",
    ],
    "Tricholoma terreum": [
      "Greyish cap with radial fibrous scales, up to 8 cm; white-grey notched gills",
      "Mild floury smell; grows EXCLUSIVELY under pines (obligate symbiosis)",
      "Avoid Tricholoma pardinum ☠️ (cap up to 15 cm, strong rancid-flour smell, very dense white gills)",
    ],
    "Armillaria mellea": [
      "Honey-brown cap up to 15 cm with dark scales in the centre; white gills that stain brown",
      "Stem with a persistent white-yellowish membranous RING; grows in tufts at the base of trunks",
      "Black rhizomorphs (cords) visible nearby; NEEDS at least 30 min of cooking, never raw",
    ],
    "Calocybe gambosa": [
      "Robust white-cream cap up to 12 cm; very dense, crowded white gills",
      "STRONG SMELL of fresh flour — the most characteristic sign of this species",
      "Grows in spring in rings in meadows; avoid Entoloma sinuatum ☠️ (fruity smell, pinkish gills)",
    ],
    "Amanita phalloides": [
      "⚠️ DEADLY: olive-green or greyish cap; free, dense white gills; stem with an amber ring",
      "⚠️ WHITE SAC-LIKE VOLVA at the base — always look for it, it may be buried underground",
      "⚠️ A single cap can kill an adult; no antidote; symptoms take 6-12 h (too late)",
    ],
    "Amanita muscaria": [
      "⚠️ Bright red cap with white patches (veil remnants); free white gills",
      "⚠️ Bulbous base with volva remnants in concentric WHITE RINGS; hanging white ring",
      "⚠️ Causes hallucinations, delirium and kidney damage; no specific antidote",
    ],
    "Amanita virosa": [
      "⚠️ DEADLY: completely WHITE — cap, gills, stem and volva; conical cap when young",
      "⚠️ Persistent unpleasant smell; large sac-like volva; white membranous ring",
      "⚠️ Never eat anything completely white from the woods without expert identification — this is the Destroying Angel",
    ],
    "Galerina marginata": [
      "⚠️ Small honey-brown mushroom up to 4 cm; brown gills; brown membranous ring on the stem",
      "⚠️ Grows in groups on conifer wood, similar to Armillaria mellea but much smaller",
      "⚠️ Contains AMATOXINS in the same lethal dose as A. phalloides; never pick small brown mushrooms on wood",
    ],
    "Cortinarius rubellus": [
      "⚠️ Conical-convex red-brown cap up to 8 cm; brown-orange gills; fibrous cortina remnants on the stem",
      "⚠️ Rusty-brown spores; grows in spruce and birch woods",
      "⚠️ Contains ORELLANINE: symptoms appear 2-3 WEEKS LATER, when kidney damage is already irreversible",
    ],
    "Omphalotus olearius": [
      "⚠️ Intense orange-yellow cap up to 15 cm; bright orange gills that GLOW at night",
      "⚠️ ALWAYS grows in dense tufts (5-30 specimens) at the foot of olive and holm oak trees; never solitary",
      "⚠️ TRUE gills (not forked folds like the chanterelle); strong smell of rotten wood",
    ],
    "Inocybe erubescens": [
      "⚠️ WHITE conical-umbonate cap that progressively reddens when touched and with age",
      "⚠️ Unpleasant smell of damp earth; grows in spring in parks with lime and yew trees",
      "⚠️ Contains MUSCARINE in high concentration; white flesh reddening on touch is the key sign",
    ],
    "Hypholoma fasciculare": [
      "⚠️ Sulphur-yellow cap up to 7 cm; yellowish-olive gills; grows in dense tufts on wood",
      "⚠️ EXTREMELY BITTER TASTE (just touching it to the tongue is enough to notice)",
      "⚠️ Do not confuse with Armillaria mellea: Hypholoma has olive gills and a bitter taste, no cream tones towards the base",
    ],
    "Scleroderma citrinum": [
      "⚠️ Hard round-flattened body (like a potato), beige-yellow with brown scales; no distinct stem",
      "⚠️ Interior BLACK-VIOLET when mature — edible Lycoperdon puffballs always have a uniformly white interior",
      "⚠️ Strong unpleasant smell; grows half-buried in sandy soils under pines and oaks",
    ],
    "Amanita rubescens": [
      "Brown-pinkish cap with irregular grey-pink patches (universal veil remnants)",
      "White flesh that clearly REDDENS when cut and at insect bites — the definitive sign of the species",
      "Striate ring and bulbous base with plates (no sac); edible when cooked but toxic raw",
    ],
    "Russula virescens": [
      "Green-bluish cap with skin CRACKED INTO PLAQUES (ceramic mosaic look) — unmistakable",
      "White-cream gills, stout white stem, firm flesh that does not change colour when cut",
      "Sweet or slightly bitter taste; mild-tasting Russulas with white gills are usually edible",
    ],
    "Lycoperdon perlatum": [
      "White-cream inverted-pear-shaped body, covered in small white granules that rub off",
      "Cut it in half: COMPLETELY WHITE and uniform interior = edible; any internal structure = discard",
      "When mature it turns yellow-olive and the apex opens releasing spores; no longer edible at that stage",
    ],
    "Cerioporus squamosus": [
      "Large cap up to 60 cm, ochre with concentric brown scales; LARGE ANGULAR white pores underneath",
      "Short off-centre stem, black at the base; grows on living or dead poplars, ash and aspen",
      "Pick YOUNG (white tender flesh); when mature it is as hard as wood",
    ],
    "Laetiporus sulphureus": [
      "Bracket fungus in overlapping intense SULPHUR-YELLOW rosettes, up to 40 cm; small yellow pores underneath",
      "Grows at the base of oaks, cherry trees and conifers; firm succulent white flesh when young",
      "Young (bright and flexible) it is excellent cooked; mature (dull and soft) it is bitter and indigestible",
    ],
    "Agrocybe praecox": [
      "Brown-cream cap up to 7 cm; dark CHERRY-BROWN gills when mature (brown spores)",
      "Characteristic floury smell; grows in spring in meadows, path edges and gardens",
      "Fragile membranous ring that soon disappears; the brown spore-coloured gills set it apart",
    ],
    "Disciotis venosa": [
      "Large disc-shaped brown-ochre cup up to 20 cm; upper surface with prominent VEINS AND RIDGES",
      "Pale granular outer surface; grows in spring in riverside woods and beech forests",
      "⚠️ Smells of bleach when rubbed; needs 30 min of cooking to remove helvellic acid; NEVER raw",
    ],
    "Strobilurus tenacellus": [
      "Small brown mushroom up to 2 cm; grows EXCLUSIVELY on buried or half-buried pine CONES",
      "Very long thin stem, cartilaginous and tough (bends without breaking); attached to the cone",
      "Growth on a pine cone + tough unbreakable stem make it unmistakable; too small to cook",
    ],
    "Sarcosphaera coronaria": [
      "⚠️ Large cup up to 15 cm that splits into an irregular star exposing an intense LILAC-VIOLET interior",
      "Grows half-buried in mountain pine woods in early spring, often near snow",
      "⚠️ Toxic raw; even cooked it can cause reactions in some people — best avoided",
    ],
    "Boletus pinophilus": [
      "Dark red-brown cap up to 25 cm; white-cream pores that age yellow-greenish",
      "Swollen brown stem with a fine net at the top; flesh NEVER turns blue when cut",
      "Grows EXCLUSIVELY under pines; excellent smell and taste, equivalent to the cep",
    ],
    "Suillus luteus": [
      "Chocolate cap, VERY SLIMY when wet, up to 10 cm; small yellow pores under the cap",
      "Prominent persistent membranous RING hanging on the stem; stem with dark dots above the ring",
      "Always under two-needled pines; remove the slimy skin before cooking (it can cause digestive upset)",
    ],
    "Leccinum scabrum": [
      "Brown-greyish cap up to 15 cm; small white pores; stout stem with unmistakable BLACK SCALES",
      "White flesh slowly turning grey-pink when cut (not blue); ALWAYS grows under birches",
      "The black scales on the stem (like ground pepper) make it very recognisable",
    ],
    "Hygrophorus marzuolus": [
      "Grey cap up to 12 cm, convex then depressed; THICK, widely spaced white-grey gills",
      "Fruits very early in spring, even WITH SNOW; exclusively under fir or mountain pine",
      "Grey-white stem, mild smell; one of the first mushrooms of the mountain spring season",
    ],
    "Gymnosporangium clavariiforme": [
      "🌱 Parasite with alternating hosts: forms ORANGE JELLY masses on juniper branches in spring",
      "🌱 In summer it parasitises apple and pear leaves, forming yellow-orange spots with aecia",
      "🌱 The orange jelly on juniper (Juniperus) is very showy but is not an edible mushroom",
    ],
    "Triphragmium ulmariae": [
      "🌱 Parasite of meadowsweet (Filipendula ulmaria); forms brown-orange pustules on the underside of leaves",
      "🌱 Forms no macroscopic fruiting body; identified by the pustules on Filipendula in damp places",
      "🌱 No edible interest; the three-celled spores require microscopy",
    ],
    "Microbotryum pustulatum": [
      "🌱 Plant smut: infects Silene and other Caryophyllaceae, turning the stamens into masses of black spores",
      "🌱 Forms no mushroom; the infection shows as blackened flowers of the affected plant",
      "🌱 No edible interest; host plant + blackened reproductive parts = diagnosis",
    ],
    "Kretzschmaria deusta": [
      "Fungus forming a HARD BLACK CRUST on stumps, with a white-grey margin when actively growing",
      "Young it is white-greyish and soft; it hardens and blackens with age",
      "Internal parasite of deciduous trees causing white heart rot; not edible",
    ],
  },
  "de": {
    "Boletus edulis": [
      "Kastanienbrauner Hut bis 25 cm, glatt und trocken; weisse Poren, die im Alter gelb-oliv werden",
      "Kräftiger Stiel mit feinem weissem Netz im oberen Teil; Fleisch verfärbt sich beim Schnitt NIE blau",
      "Süsslicher Nussgeruch, milder Geschmack; wächst unter Föhren, Tannen und Eichen von September bis November",
    ],
    "Lactarius deliciosus": [
      "Orangeroter Hut mit deutlich konzentrischen Zonen; dichte orange Lamellen",
      "Beim Anschneiden der Lamellen tritt reichlich orange Milch aus; nach 15-20 Min. grüne Flecken",
      "Kurzer, kräftiger Stiel mit orangen Grübchen; wächst IMMER unter Föhren",
    ],
    "Cantharellus cibarius": [
      "Dottergelber, welliger Hut bis 10 cm; gegabelte, verzweigte LEISTEN (keine Lamellen), die am Stiel herablaufen",
      "Fruchtiger Aprikosengeruch, festes weisses Fleisch; wächst im Herbst in Buchen- und Eichenwäldern",
      "Die Leisten lassen sich nicht vom Hut lösen; Verwechslung mit Omphalotus olearius ☠️ vermeiden (echte Lamellen, leuchtend orange, büschelig auf Holz)",
    ],
    "Macrolepiota procera": [
      "Grosser Hut bis 30 cm mit braunen Schuppen auf weissem Grund; markanter brauner Buckel in der Mitte",
      "Stiel mit doppeltem, verschiebbarem Ring und braun-weisser Natterung; knollige Basis",
      "Weisses Fleisch, das sich beim Schnitt nicht verfärbt, angenehmer Geruch; nur den Hut sammeln, der Stiel ist zu zäh",
    ],
    "Agaricus campestris": [
      "Weiss-gräulicher Hut bis 10 cm; Lamellen zuerst KRÄFTIG ROSA, im Alter braun-schwarz",
      "Stiel mit einfachem, vergänglichem Ring; Fleisch rötet beim Schnitt leicht",
      "Wächst auf WIESEN und Weiden (nie im Wald); Agaricus xanthodermus ☠️ vermeiden, der beim Schnitt gilbt und nach Tinte riecht",
    ],
    "Hydnum repandum": [
      "Unterseite mit weiss-cremefarbenen STACHELN (keine Lamellen oder Poren) — einzigartiges Stachel-Hymenophor",
      "Unregelmässiger, blassbrauner Hut bis 15 cm; festes weisses Fleisch, leicht bitter (durch Blanchieren behebbar)",
      "Dank der weissen Stacheln unverwechselbar; wächst im Herbst gruppenweise in Laubwäldern",
    ],
    "Craterellus cornucopioides": [
      "Schwarz-graue Trompetenform, bis 12 cm; der Fruchtkörper ist innen völlig HOHL",
      "Intensiver, sehr angenehmer Trockenfrüchte-Geruch, der beim Trocknen bleibt; wächst in dichten Kolonien",
      "Zwischen Laub sehr schwer zu sehen; in feuchten Herbsten unter Eichen suchen",
    ],
    "Morchella esculenta": [
      "Kegelig-eiförmiger Hut mit unregelmässigen Gruben und Rippen; aufschneiden: Stiel und Hut bilden ein durchgehend HOHLES Stück",
      "Angenehmer Geruch; wächst im Frühling in Eschenwäldern, alten Obstgärten und feuchten Auen",
      "IMMER mindestens 30 Min. kochen — roh enthalten sie Helvellasäure, die schweres Erbrechen verursacht",
    ],
    "Pleurotus ostreatus": [
      "Austernförmiger, grau-bläulicher Hut bis 25 cm; weisse, HERABLAUFENDE Lamellen",
      "Wächst in übereinanderliegenden Rosetten an Laubholzstämmen (Steineiche, Buche, Pappel); ganzjährig",
      "Kurzer, seitlicher Stiel ohne Ring; angenehmer Geruch und festes weisses Fleisch",
    ],
    "Tricholoma terreum": [
      "Gräulicher Hut mit radialfaserigen Schuppen, bis 8 cm; weiss-graue, ausgebuchtete Lamellen",
      "Milder Mehlgeruch; wächst AUSSCHLIESSLICH unter Föhren (obligate Symbiose)",
      "Tricholoma pardinum ☠️ vermeiden (Hut bis 15 cm, starker ranziger Mehlgeruch, sehr dichte weisse Lamellen)",
    ],
    "Armillaria mellea": [
      "Honigbrauner Hut bis 15 cm mit dunklen Schuppen in der Mitte; weisse Lamellen, die braun flecken",
      "Stiel mit beständigem, weiss-gelblichem häutigem RING; wächst büschelig am Stammgrund",
      "Schwarze Rhizomorphen (Stränge) in der Umgebung sichtbar; mindestens 30 Min. kochen, nie roh",
    ],
    "Calocybe gambosa": [
      "Kräftiger weiss-cremefarbener Hut bis 12 cm; sehr dichte, gedrängte weisse Lamellen",
      "STARKER GERUCH nach frischem Mehl — das typischste Merkmal dieser Art",
      "Wächst im Frühling in Ringen auf Wiesen; Entoloma sinuatum ☠️ vermeiden (fruchtiger Geruch, rosa Lamellen)",
    ],
    "Amanita phalloides": [
      "⚠️ TÖDLICH: oliv-grüner oder gräulicher Hut; freie, dichte weisse Lamellen; Stiel mit bernsteinfarbenem Ring",
      "⚠️ WEISSE, SACKARTIGE VOLVA an der Basis — immer danach suchen, sie kann im Boden vergraben sein",
      "⚠️ Ein einziger Hut kann einen Erwachsenen töten; kein Gegengift; Symptome erst nach 6-12 h (zu spät)",
    ],
    "Amanita muscaria": [
      "⚠️ Leuchtend roter Hut mit weissen Flocken (Velumreste); freie weisse Lamellen",
      "⚠️ Knollige Basis mit Volvaresten in konzentrischen WEISSEN RINGEN; hängender weisser Ring",
      "⚠️ Verursacht Halluzinationen, Delirien und Nierenschäden; kein spezifisches Gegengift",
    ],
    "Amanita virosa": [
      "⚠️ TÖDLICH: vollständig WEISS — Hut, Lamellen, Stiel und Volva; Hut jung kegelig",
      "⚠️ Anhaltend unangenehmer Geruch; grosse sackartige Volva; weisser häutiger Ring",
      "⚠️ Nie etwas völlig Weisses aus dem Wald ohne Expertenbestimmung essen — der Kegelhütige Knollenblätterpilz",
    ],
    "Galerina marginata": [
      "⚠️ Kleiner honigbrauner Pilz bis 4 cm; braune Lamellen; brauner häutiger Ring am Stiel",
      "⚠️ Wächst gruppenweise auf Nadelholz, ähnlich dem Hallimasch, aber viel kleiner",
      "⚠️ Enthält AMATOXINE in derselben tödlichen Dosis wie A. phalloides; nie kleine braune Pilze auf Holz sammeln",
    ],
    "Cortinarius rubellus": [
      "⚠️ Kegelig-gewölbter rotbrauner Hut bis 8 cm; braun-orange Lamellen; faserige Cortinareste am Stiel",
      "⚠️ Rostbraune Sporen; wächst in Fichten- und Birkenwäldern",
      "⚠️ Enthält ORELLANIN: Symptome erst 2-3 WOCHEN SPÄTER, wenn der Nierenschaden bereits irreversibel ist",
    ],
    "Omphalotus olearius": [
      "⚠️ Intensiv orange-gelber Hut bis 15 cm; leuchtend orange Lamellen, die nachts LEUCHTEN",
      "⚠️ Wächst IMMER in dichten Büscheln (5-30 Stück) am Fuss von Oliven- und Steineichen; nie einzeln",
      "⚠️ ECHTE Lamellen (keine gegabelten Leisten wie beim Eierschwamm); starker Geruch nach faulem Holz",
    ],
    "Inocybe erubescens": [
      "⚠️ WEISSER, kegelig-gebuckelter Hut, der bei Berührung und im Alter zunehmend rötet",
      "⚠️ Unangenehmer Geruch nach feuchter Erde; wächst im Frühling in Parks mit Linden und Eiben",
      "⚠️ Enthält MUSCARIN in hoher Konzentration; das Röten des weissen Fleisches bei Berührung ist das Schlüsselmerkmal",
    ],
    "Hypholoma fasciculare": [
      "⚠️ Schwefelgelber Hut bis 7 cm; gelblich-olive Lamellen; wächst in dichten Büscheln auf Holz",
      "⚠️ EXTREM BITTERER GESCHMACK (schon die Berührung mit der Zunge genügt)",
      "⚠️ Nicht mit dem Hallimasch verwechseln: Hypholoma hat olive Lamellen und schmeckt bitter, keine Cremetöne zur Basis hin",
    ],
    "Scleroderma citrinum": [
      "⚠️ Harter, rundlich-abgeflachter Körper (wie eine Kartoffel), beige-gelb mit braunen Schuppen; kein abgesetzter Stiel",
      "⚠️ Inneres reif SCHWARZ-VIOLETT — essbare Boviste (Lycoperdon) sind innen immer gleichmässig weiss",
      "⚠️ Starker unangenehmer Geruch; wächst halb eingegraben in sandigen Böden unter Föhren und Eichen",
    ],
    "Amanita rubescens": [
      "Braun-rosaliche Hut mit unregelmässigen grau-rosa Flecken (Reste des Velum universale)",
      "Weisses Fleisch, das beim Schnitt und an Frassstellen deutlich RÖTET — das entscheidende Artmerkmal",
      "Geriefter Ring und knollige Basis mit Gürteln (kein Sack); gekocht essbar, roh giftig",
    ],
    "Russula virescens": [
      "Grün-bläulicher Hut mit FELDERIG AUFGERISSENER Haut (Keramikmosaik-Optik) — unverwechselbar",
      "Weiss-cremefarbene Lamellen, kräftiger weisser Stiel, festes Fleisch ohne Verfärbung beim Schnitt",
      "Milder oder leicht bitterer Geschmack; mild schmeckende Täublinge mit weissen Lamellen sind meist essbar",
    ],
    "Lycoperdon perlatum": [
      "Weiss-cremefarbener, umgekehrt birnenförmiger Körper, mit kleinen weissen Warzen, die sich abreiben lassen",
      "Halbieren: VÖLLIG WEISSES, gleichmässiges Inneres = essbar; jede innere Struktur = verwerfen",
      "Reif wird er gelb-oliv und die Spitze öffnet sich zur Sporenabgabe; dann nicht mehr essbar",
    ],
    "Cerioporus squamosus": [
      "Grosser Hut bis 60 cm, ocker mit konzentrischen braunen Schuppen; GROSSE, ECKIGE weisse Poren unterseits",
      "Kurzer, seitlicher, an der Basis schwarzer Stiel; wächst an lebenden oder toten Pappeln, Eschen und Espen",
      "JUNG sammeln (weisses, zartes Fleisch); reif ist er holzhart",
    ],
    "Laetiporus sulphureus": [
      "Porling in übereinanderliegenden, intensiv SCHWEFELGELBEN Rosetten, bis 40 cm; kleine gelbe Poren unterseits",
      "Wächst am Fuss von Eichen, Kirschbäumen und Nadelbäumen; jung festes, saftiges weisses Fleisch",
      "Jung (leuchtend und biegsam) gekocht ausgezeichnet; alt (matt und weich) bitter und unverdaulich",
    ],
    "Agrocybe praecox": [
      "Braun-cremefarbener Hut bis 7 cm; reif dunkel KIRSCHBRAUNE Lamellen (braune Sporen)",
      "Charakteristischer Mehlgeruch; wächst im Frühling auf Wiesen, an Wegrändern und in Gärten",
      "Vergänglicher häutiger Ring; die braunen, sporenfarbenen Lamellen unterscheiden ihn von anderen",
    ],
    "Disciotis venosa": [
      "Grosse, scheibenförmige braun-ockerfarbene Schale bis 20 cm; Oberseite mit auffälligen ADERN UND RIPPEN",
      "Blasse, körnige Aussenseite; wächst im Frühling in Auwäldern und Buchenwäldern",
      "⚠️ Riecht beim Reiben nach Chlor; 30 Min. kochen, um die Helvellasäure zu entfernen; NIE roh",
    ],
    "Strobilurus tenacellus": [
      "Kleiner brauner Pilz bis 2 cm; wächst AUSSCHLIESSLICH auf vergrabenen oder halb vergrabenen FÖHRENZAPFEN",
      "Sehr langer, dünner, knorpelig-zäher Stiel (biegt sich, ohne zu brechen); am Zapfen befestigt",
      "Wuchs auf Zapfen + zäher, unzerbrechlicher Stiel machen ihn unverwechselbar; zu klein zum Kochen",
    ],
    "Sarcosphaera coronaria": [
      "⚠️ Grosse Schale bis 15 cm, die sternförmig aufreisst und ein intensiv LILA-VIOLETTES Inneres freigibt",
      "Wächst halb eingegraben in Bergföhrenwäldern im zeitigen Frühling, oft nahe am Schnee",
      "⚠️ Roh giftig; auch gekocht kann er bei manchen Menschen Reaktionen auslösen — besser meiden",
    ],
    "Boletus pinophilus": [
      "Dunkel rotbrauner Hut bis 25 cm; weiss-cremefarbene Poren, die im Alter gelb-grünlich werden",
      "Bauchiger brauner Stiel mit feinem Netz im oberen Teil; Fleisch verfärbt sich beim Schnitt NIE blau",
      "Wächst AUSSCHLIESSLICH unter Föhren; hervorragender Geruch und Geschmack, dem Steinpilz ebenbürtig",
    ],
    "Suillus luteus": [
      "Schokoladenbrauner, bei Nässe SEHR SCHLEIMIGER Hut bis 10 cm; kleine gelbe Poren unter dem Hut",
      "Auffälliger, beständiger häutiger RING am Stiel; Stiel oberhalb des Rings dunkel punktiert",
      "Immer unter zweinadeligen Föhren; die schleimige Huthaut vor dem Kochen abziehen (kann Verdauungsbeschwerden verursachen)",
    ],
    "Leccinum scabrum": [
      "Braun-gräulicher Hut bis 15 cm; kleine weisse Poren; kräftiger Stiel mit unverwechselbaren SCHWARZEN SCHUPPEN",
      "Weisses Fleisch, das beim Schnitt langsam grau-rosa wird (nicht blau); wächst IMMER unter Birken",
      "Die schwarzen Stielschuppen (wie gemahlener Pfeffer) machen ihn sehr gut erkennbar",
    ],
    "Hygrophorus marzuolus": [
      "Grauer Hut bis 12 cm, gewölbt bis vertieft; DICKE, entfernt stehende weiss-graue Lamellen",
      "Erscheint sehr früh im Frühling, sogar BEI SCHNEE; ausschliesslich unter Tanne oder Bergföhre",
      "Grau-weisser Stiel, milder Geruch; einer der ersten Pilze der Frühjahrssaison in den Bergen",
    ],
    "Gymnosporangium clavariiforme": [
      "🌱 Wirtswechselnder Parasit: bildet im Frühling ORANGE GALLERTMASSEN an Wacholderzweigen",
      "🌱 Im Sommer befällt er Apfel- und Birnenblätter und bildet gelb-orange Flecken mit Aecidien",
      "🌱 Die orange Gallerte auf Wacholder (Juniperus) ist sehr auffällig, aber kein Speisepilz",
    ],
    "Triphragmium ulmariae": [
      "🌱 Parasit des Mädesüss (Filipendula ulmaria); bildet braun-orange Pusteln auf der Blattunterseite",
      "🌱 Kein makroskopischer Fruchtkörper; erkennbar an den Pusteln auf Filipendula an feuchten Standorten",
      "🌱 Nicht essbar; die dreizelligen Sporen erfordern ein Mikroskop",
    ],
    "Microbotryum pustulatum": [
      "🌱 Pflanzenbrand: befällt Silene und andere Nelkengewächse und verwandelt die Staubblätter in schwarze Sporenmassen",
      "🌱 Bildet keinen Pilz; die Infektion zeigt sich an geschwärzten Blüten der befallenen Pflanze",
      "🌱 Nicht essbar; Wirtspflanze + geschwärzte Fortpflanzungsorgane = Diagnose",
    ],
    "Kretzschmaria deusta": [
      "Pilz in Form einer HARTEN SCHWARZEN KRUSTE auf Stümpfen, mit weiss-grauem Rand während des Wachstums",
      "Jung weiss-gräulich und weich; wird mit dem Alter hart und schwarz",
      "Innerer Parasit von Laubbäumen, verursacht Weissfäule im Kern; nicht essbar",
    ],
  },
}

GENUS_TIPS_I18N = {
  "en": {
    "Amanita": [
      "⚠️ ALWAYS check for a VOLVA (sac) at the base — buried or not; it is the most dangerous sign of the genus",
      "Look for a ring on the stem and whether the gills are FREE (not reaching the stem)",
      "⚠️ Never eat any Amanita without expert confirmation — the genus includes the most lethal species in the world",
    ],
    "Boletus": [
      "Check whether the flesh or pores turn blue or red when cut — a warning sign in many species",
      "Look at the pore colour (underneath): white/cream = generally safe; red/orange = caution",
      "The absence of gills (spongy pores instead) is characteristic of the Boletaceae group",
    ],
    "Russula": [
      "The white-cream gills break easily (very brittle); short stout stem",
      "Taste a tiny piece of gill: if it is VERY HOT or very bitter, discard the species",
      "Peel the cuticle: if it peels easily and evenly it is a clue; mild taste = generally good",
    ],
    "Lactarius": [
      "Cut the cap or the gills: the LATEX (milky liquid) that appears is the definitive sign of the genus",
      "Check the COLOUR of the latex (white, yellow, orange, colourless) and whether it changes in the air",
      "The gills are decurrent; the host tree is key to identifying the species",
    ],
    "Cortinarius": [
      "⚠️ A very large genus with DEADLY species (orellanine, no antidote); rusty-brown spores",
      "Look for REMNANTS OF A FIBROUS CORTINA (cobweb-like veil) on the stem — the sign of the genus",
      "⚠️ Orellanine symptoms appear 2-3 WEEKS LATER; never eat any Cortinarius",
    ],
    "Inocybe": [
      "⚠️ A genus with many TOXIC species (muscarine); radially fibrillose cap, brown gills",
      "Smell of rancid flour, damp earth or sperm; brown warty spores",
      "⚠️ Very hard to tell apart even with a microscope; better not to eat any Inocybe",
    ],
    "Tricholoma": [
      "Gills NOTCHED where they meet the stem; most are white, grey or yellow",
      "The host tree is strict (under pines or under deciduous trees, not mixed); always check it",
      "Some species are very toxic (T. pardinum, T. equestre); species-level identification is essential",
    ],
    "Pleurotus": [
      "Lateral growth on WOOD (off-centre or absent stem); decurrent gills (running down the stem)",
      "Oyster- or fan-shaped cap; pleasant smell and firm white flesh",
      "Confirm it grows on wood (not on soil); species of this genus are generally edible",
    ],
    "Galerina": [
      "⚠️ A genus with LETHAL species (amatoxins, the same toxin as A. phalloides)",
      "Brown spores (visible rusty dust); fragile brown membranous ring on the upper stem",
      "⚠️ Never pick small brown mushrooms on wood without complete expert identification",
    ],
    "Puccinia": [
      "🌱 PLANT PARASITE fungus (rust); forms orange, brown or black pustules on leaves",
      "🌱 Not a macroscopic mushroom — it sporulates on the surfaces of specific host plants",
      "🌱 No culinary interest; identified by the host plant and the type of pustules",
    ],
    "Taphrina": [
      "🌱 Parasite causing DEFORMATIONS of leaves and fruits (peach leaf curl, pocket plums)",
      "🌱 Forms no fruiting body; the infection shows as swellings or deformations of the host plant",
      "🌱 No edible interest; identified by the host plant and the type of deformation",
    ],
    "Erysiphe": [
      "🌱 POWDERY MILDEW fungus: forms a white powdery layer on leaves and stems",
      "🌱 Forms no mushroom; seen as white dust on the plant surface",
      "🌱 No culinary interest; each Erysiphe species is specific to a plant host",
    ],
    "Gymnosporangium": [
      "🌱 Parasite with ALTERNATING HOSTS: Juniperus (juniper) + Rosaceae (apple, hawthorn)",
      "🌱 On juniper it forms orange jelly galls in spring; on Rosaceae, leaf spots",
      "🌱 The orange jelly on juniper is very showy but is not an edible mushroom",
    ],
    "Microbotryum": [
      "🌱 Plant smut: turns reproductive parts into masses of BLACK spores",
      "🌱 Forms no fruiting body; the infection shows in blackened flowers or seeds",
      "🌱 No edible interest; identified by the affected host plant",
    ],
    "Parmotrema": [
      "🪨 Large foliose lichen, grey-green on the upper side, WHITE underneath",
      "🪨 Grows on rocks and bark; indicates CLEAN air (very sensitive to SO₂ pollution)",
      "🪨 Not a mushroom but a fungus + alga symbiosis; no culinary interest",
    ],
    "Circinaria": [
      "🪨 CRUSTOSE lichen growing tightly attached to limestone rocks; forms grey-brown rosettes",
      "🪨 Very hard to separate from the substrate; indicates a long-stable environment",
      "🪨 Not a mushroom; precise identification requires microscopy and chemical tests",
    ],
    "Usnea": [
      "🪨 HANGING grey-green fruticose lichen on branches; key sign: an ELASTIC CENTRAL CORD visible when stretched",
      "🪨 Excellent air-quality indicator; its presence confirms low pollution",
      "🪨 Medicinal (antibacterial usnic acid) but not edible",
    ],
  },
  "de": {
    "Amanita": [
      "⚠️ IMMER die VOLVA (Sack) an der Basis prüfen — vergraben oder nicht; das gefährlichste Merkmal der Gattung",
      "Auf einen Ring am Stiel achten und darauf, ob die Lamellen FREI sind (den Stiel nicht erreichen)",
      "⚠️ Nie einen Wulstling ohne Expertenbestätigung essen — die Gattung enthält die tödlichsten Arten der Welt",
    ],
    "Boletus": [
      "Prüfen, ob Fleisch oder Poren beim Schnitt blauen oder röten — bei vielen Arten ein Warnzeichen",
      "Porenfarbe (unterseits) beachten: weiss/creme = meist unbedenklich; rot/orange = Vorsicht",
      "Das Fehlen von Lamellen (stattdessen schwammige Poren) ist typisch für die Boletaceae",
    ],
    "Russula": [
      "Die weiss-cremefarbenen Lamellen brechen leicht (sehr spröde); kurzer, kräftiger Stiel",
      "Ein winziges Stück Lamelle kosten: SEHR SCHARF oder sehr bitter → Art verwerfen",
      "Huthaut abziehen: lässt sie sich leicht und gleichmässig abziehen, ist das ein Hinweis; milder Geschmack = meist gut",
    ],
    "Lactarius": [
      "Hut oder Lamellen anschneiden: die austretende MILCH ist das entscheidende Merkmal der Gattung",
      "FARBE der Milch prüfen (weiss, gelb, orange, farblos) und ob sie sich an der Luft verändert",
      "Lamellen herablaufend; der Wirtsbaum ist der Schlüssel zur Artbestimmung",
    ],
    "Cortinarius": [
      "⚠️ Sehr grosse Gattung mit TÖDLICHEN Arten (Orellanin, kein Gegengift); rostbraune Sporen",
      "Auf RESTE EINER FASERIGEN CORTINA (spinnwebartiger Schleier) am Stiel achten — das Gattungsmerkmal",
      "⚠️ Orellanin-Symptome treten 2-3 WOCHEN SPÄTER auf; nie einen Schleierling essen",
    ],
    "Inocybe": [
      "⚠️ Gattung mit vielen GIFTIGEN Arten (Muscarin); radialfaseriger Hut, braune Lamellen",
      "Geruch nach ranzigem Mehl, feuchter Erde oder Sperma; braune, warzige Sporen",
      "⚠️ Selbst mit Mikroskop schwer zu unterscheiden; besser keinen Risspilz essen",
    ],
    "Tricholoma": [
      "Lamellen am Stiel AUSGEBUCHTET; meist weiss, grau oder gelb",
      "Strenger Wirtsbaum (unter Föhren oder unter Laubbäumen, nicht gemischt); immer prüfen",
      "Einige Arten sehr giftig (T. pardinum, T. equestre); Bestimmung auf Artniveau ist unerlässlich",
    ],
    "Pleurotus": [
      "Seitliches Wachstum auf HOLZ (Stiel seitlich oder fehlend); herablaufende Lamellen",
      "Austern- oder fächerförmiger Hut; angenehmer Geruch und festes weisses Fleisch",
      "Sicherstellen, dass er auf Holz wächst (nicht auf Erde); die Arten der Gattung sind meist essbar",
    ],
    "Galerina": [
      "⚠️ Gattung mit TÖDLICHEN Arten (Amatoxine, dasselbe Gift wie A. phalloides)",
      "Braune Sporen (rostiger Staub sichtbar); vergänglicher brauner häutiger Ring im oberen Stielteil",
      "⚠️ Nie kleine braune Pilze auf Holz ohne vollständige Expertenbestimmung sammeln",
    ],
    "Puccinia": [
      "🌱 PFLANZENPARASIT (Rostpilz); bildet orange, braune oder schwarze Pusteln auf Blättern",
      "🌱 Kein makroskopischer Pilz — sporuliert auf der Oberfläche bestimmter Wirtspflanzen",
      "🌱 Kein kulinarisches Interesse; Bestimmung über Wirtspflanze und Pustelform",
    ],
    "Taphrina": [
      "🌱 Parasit, der VERFORMUNGEN an Blättern und Früchten verursacht (Kräuselkrankheit, Narrentaschen)",
      "🌱 Kein Fruchtkörper; die Infektion zeigt sich als Schwellungen oder Verformungen der Wirtspflanze",
      "🌱 Nicht essbar; Bestimmung über Wirtspflanze und Art der Verformung",
    ],
    "Erysiphe": [
      "🌱 ECHTER MEHLTAU: bildet einen weissen, pudrigen Belag auf Blättern und Stängeln",
      "🌱 Bildet keinen Pilz; als weisser Staub auf der Pflanzenoberfläche sichtbar",
      "🌱 Kein kulinarisches Interesse; jede Erysiphe-Art ist an eine Wirtspflanze gebunden",
    ],
    "Gymnosporangium": [
      "🌱 Parasit mit WIRTSWECHSEL: Juniperus (Wacholder) + Rosengewächse (Apfel, Weissdorn)",
      "🌱 Auf Wacholder im Frühling orange Gallertgallen; auf Rosengewächsen Blattflecken",
      "🌱 Die orange Gallerte auf Wacholder ist sehr auffällig, aber kein Speisepilz",
    ],
    "Microbotryum": [
      "🌱 Pflanzenbrand: verwandelt Fortpflanzungsorgane in SCHWARZE Sporenmassen",
      "🌱 Kein Fruchtkörper; die Infektion zeigt sich an geschwärzten Blüten oder Samen",
      "🌱 Nicht essbar; Bestimmung über die befallene Wirtspflanze",
    ],
    "Parmotrema": [
      "🪨 Grosse Blattflechte, oberseits grau-grün, unterseits WEISS",
      "🪨 Wächst auf Felsen und Rinde; zeigt SAUBERE Luft an (sehr empfindlich gegen SO₂)",
      "🪨 Kein Pilz, sondern eine Symbiose aus Pilz und Alge; kein kulinarisches Interesse",
    ],
    "Circinaria": [
      "🪨 KRUSTENFLECHTE, fest auf Kalkfelsen; bildet grau-braune Rosetten",
      "🪨 Kaum vom Substrat zu lösen; zeigt lange Stabilität des Standorts an",
      "🪨 Kein Pilz; genaue Bestimmung erfordert Mikroskopie und chemische Tests",
    ],
    "Usnea": [
      "🪨 HÄNGENDE grau-grüne Strauchflechte an Ästen; Schlüsselmerkmal: ein ELASTISCHER ZENTRALSTRANG, sichtbar beim Dehnen",
      "🪨 Hervorragender Luftgüte-Indikator; ihr Vorkommen bestätigt geringe Verschmutzung",
      "🪨 Medizinisch (antibakterielle Usninsäure), aber nicht essbar",
    ],
  },
}
