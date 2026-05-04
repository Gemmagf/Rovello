# Estudi comparatiu: millor IA per detectar bolets

**Data:** 2026-04-30
**Objectiu:** Triar el millor model per identificació fine-grained d'espècies de bolets a Catalunya i Suïssa, amb el màxim d'espècies possible, entrenat localment a MacBook Air M4 (32GB RAM, GPU 10 cores, MPS).

---

## 1. Per què és un problema fine-grained difícil

La identificació de bolets té tres reptes específics:

1. **Diferències sub-classe molt subtils:** *Amanita phalloides* (mortal) vs *A. citrina* (no comestible) vs *Russula virescens* (excel·lent) tenen diferències mínimes a la imatge.
2. **Variabilitat intra-classe alta:** un mateix bolet canvia molt segons edat, humitat, llum, angle.
3. **Distribució long-tail:** poques espècies tenen milers de fotos; la majoria tenen <100.

Això descarta models genèrics i exigeix:
- **Backbone amb representacions riques** (pre-entrenat en datasets grans i diversos).
- **Augmentació agressiva** (rotacions, crops, color jitter, mixup/cutmix).
- **Loss adaptat al desbalanceig** (focal loss, class-balanced sampling).
- **Senyal contextual extern** (geo + temporada → prior bayesià).

## 2. Comparativa d'arquitectures candidates

Mètriques estimades per dataset tipus FGVC (fine-grained visual classification) similar:

| Arquitectura | #Params | Top-1 estimat (200 esp.) | Throughput M4 (img/s) | VRAM training (batch 32) | Recomanació |
|---|---|---|---|---|---|
| EfficientNet-B0 (actual) | 5.3M | 78-82% | ~85 | ~3 GB | Baseline |
| EfficientNet-B3 | 12M | 82-86% | ~50 | ~6 GB | Compromís |
| **EfficientNetV2-S** | 22M | 85-89% | ~45 | ~8 GB | ✅ Bona opció |
| **ConvNeXt-Tiny** | 29M | 88-91% | ~38 | ~10 GB | ✅✅ Recomanat |
| ConvNeXt-Small | 50M | 90-92% | ~25 | ~14 GB | Si hi ha temps |
| ViT-B/16 (DeiT) | 86M | 87-91% | ~22 | ~16 GB | Necessita molts dades |
| **DINOv2 ViT-S/14 (frozen) + MLP** | 21M | 89-92% | ~50 (sols head) | ~4 GB | ✅✅✅ Si dades < 50k |
| DINOv2 ViT-B/14 fine-tuned | 86M | 92-95% | ~20 | ~18 GB | Top performance |
| BioCLIP | 86M | 84-88% | ~22 | ~16 GB | Bé per zero-shot |

### Recomanació final

**Estratègia en dos passos:**

1. **Baseline ràpid (1-2h entrenament):** `ConvNeXt-Tiny` fine-tuned amb totes les capes. Mètrica esperada: 88-91% top-1.
2. **Model definitiu (4-12h entrenament):** `DINOv2 ViT-B/14` amb fine-tuning capes finals + cap MLP. Mètrica esperada: 92-95% top-1.

DINOv2 té representacions auto-supervisades pre-entrenades amb 142M imatges naturals, i destaca especialment en fine-grained amb pocs exemples per classe — perfecte per espècies rares.

## 3. Estratègia d'entrenament

### Augmentacions
- `RandomResizedCrop(224, scale=(0.6, 1.0))`
- `RandomHorizontalFlip(p=0.5)`
- `ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1)`
- `RandomRotation(±20°)`
- `MixUp(alpha=0.2)` + `CutMix(alpha=1.0)` aleatoris
- `RandAugment(n=2, m=9)`
- Normalització ImageNet

### Hiperparàmetres
- **Optimizer:** AdamW (lr=3e-4 head, 3e-5 backbone) amb cosine decay
- **Warmup:** 5 èpoques lineal
- **Batch size:** 32 (DINOv2-B) o 64 (ConvNeXt-T) amb gradient accumulation si cal
- **Èpoques:** 50 (early stopping a 10 èpoques sense millora)
- **Loss:** CrossEntropy amb label smoothing 0.1, ponderat per inversa freq. classe
- **Mixed precision:** `torch.amp` amb MPS

### Validació
- Split 80/10/10 estratificat per espècie
- 5-fold cross-validation per al model final
- Mètriques: top-1, top-5, F1 macro, Matthews Correlation Coefficient

## 4. Integració de geolocalització i època

### Modelat del prior

Per a cada espècie *s*, construïm:

```
P(s | mes, lat, lon) ≈ KDE(observacions_GBIF[s], features=[mes, lat, lon])
```

Implementació pràctica amb dues opcions:

**Opció A — KDE multi-variable (recomanada):**
- Per cada espècie, ajustar Kernel Density Estimation sobre les observacions GBIF
- Variables: `[lat, lon, sin(2π·mes/12), cos(2π·mes/12)]` (codifica ciclicament el mes)
- Suavitzat amb Laplace per espècies amb poques observacions

**Opció B — Random Forest multi-output:**
- Input: `[lat, lon, mes_sin, mes_cos]`
- Output: distribució P(s) sobre totes les espècies
- Més robust però menys interpretable

### Fusió bayesiana

A inferència:
```python
P(s | imatge, context) ∝ P(s | imatge)^α · P(s | mes, lat, lon)^β
```

Amb `α=1.0`, `β=0.5` per defecte (l'imatge té més pes que el context). Calibrable.

Avantatges:
- Es pot actualitzar el prior sense reentrenar el CNN
- Robust si l'usuari no proporciona ubicació (β=0)
- Permet detectar incoherències ("aquest bolet diu ser X però X no apareix mai en aquesta zona/època")

## 5. Datasets per Catalunya + Suïssa

| Font | Cobertura | Dades | Format | Mida estimada |
|---|---|---|---|---|
| **iNaturalist (research-grade)** | Mundial | Imatge + GPS + data | API JSON | ~500k obs. fungi Europa |
| **GBIF** | Mundial | Coords + data (sense imatge majoritàriament) | DwC-A | ~2M obs. fungi Europa |
| **Mushroom Observer** | Mundial (focus US) | Imatge + meta | API | ~200k obs. |
| **Pl@ntNet** (api) | Mundial | Imatge + GPS | API | -- |
| **MycoDB / MycoBank** | Taxonomia | Sense imatges | -- | metadata |
| **Kaggle Mushroom1** | -- | 9 classes | Carpeta | 6k imatges |

### Estratègia de descàrrega
1. **GBIF** per al prior geo-temporal (no necessitem imatges, només coords + data + espècie). Filtre: country IN (ES, CH), kingdom=Fungi.
2. **iNaturalist** per a les imatges d'entrenament. Filtre: place_id Catalunya + Switzerland, quality_grade=research, has_photos=true.
3. **Mushroom Observer** per ampliar dataset si cal.

### Estimació final del dataset
- **Espècies amb ≥30 imatges:** ~400-600 (Catalunya+Suïssa)
- **Espècies amb ≥100 imatges:** ~150-250
- **Total imatges:** 80k-150k

## 6. Pla d'execució

| Fase | Durada estimada | Sortida |
|---|---|---|
| Descàrrega dades GBIF (priors) | 30 min | ~2M files CSV |
| Descàrrega imatges iNaturalist | 4-8 h | ~100k JPG |
| Preparació splits + augmentacions | 30 min | datasets PyTorch |
| Baseline ConvNeXt-T (50 ep) | 2-4 h amb MPS | model + mètriques |
| Model final DINOv2-B (50 ep) | 8-12 h amb MPS | model + mètriques |
| Construcció prior geo-temporal | 1 h | KDE serialitzat |
| Integració backend | 1 h | endpoint actualitzat |
| Tests i validació | 1 h | informe |

**Total:** ~20-30h de wall-time, majoritàriament desatès.

## 7. Decisions clau

✅ **Llenguatge ML:** PyTorch (millor MPS support a M4 que TensorFlow)
✅ **Backbone primari:** DINOv2 ViT-B/14
✅ **Backbone fallback:** ConvNeXt-Tiny
✅ **Prior:** KDE per espècie sobre GBIF, Catalunya+Suïssa
✅ **Fusió:** Bayesiana tardana (α/β configurables)
✅ **Cobertura:** ES (Catalunya) + CH (Suïssa)
✅ **Inferència:** mantenim Flask, afegim camps `month`, `lat`, `lon` opcionals al `/predict`
