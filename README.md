# Rovello
Aplicació web que ajuda els usuaris a identificar bolets a partir de fotos, obtenir informació detallada (diccionari), veure tips de verificació i consultar els bolets més típics segons la zona i temporada. 

## 🎯 Objectius
Educatius i informatius
Proporcionar informació segura sobre espècies de bolets.
Ajudar a diferenciar espècies comestibles de les tòxiques.
Mostrar zones i hàbitats típics.
Tecnològics
Crear una app moderna, ràpida i usable amb React.
Integrar reconeixement d’imatges amb IA.
Fer un backend escalable amb Node.js i MongoDB.
Seguretat i responsabilitat
Incloure disclaimer: l’app no substitueix un micòleg.
Alertar quan hi hagi risc de confusió amb bolets tòxics.

## 🧩 Funcionalitats clau
#### 1. Identificació per imatge
Pujar foto → enviar al backend → model IA retorna:
Predicció principal (nom bolet)
Percentatge de confiança
Llista de possibles similars

#### 2. Diccionari de bolets
Fitxa detallada amb:
Nom popular i científic
Hàbitat i temporada
Fotos de referència
Possibles confusions

#### 3. Tips de verificació
Llista de criteris per confirmar la identificació (olor, color de làmines, mida, etc.).
Avís si hi ha similars tòxics.

#### 4. Coneixement del territori
L’usuari tria zona manualment (ex: Montseny, Pirineus).
Opcional: geolocalització automàtica.
Retorn:
Bolets més típics a la zona i temporada
Hàbitats potencials (ex: “en fagedes humides trobaràs més llenegues”)

#### 5. Historial personal
Guardar identificacions fetes amb foto, lloc i data.
Opció de veure quins bolets ha trobat l’usuari en diferents zones.
🛠️ Arquitectura tècnica
Frontend: React + TailwindCSS
Backend: Node.js + Express
Base de dades: MongoDB (col·leccions: users, mushrooms, zones, identifications)
IA:
Opció 1: API externa (Plant.id, ImageVision, etc.)
Opció 2: Model propi entrenat amb TensorFlow/PyTorch
📅 Pla de treball (fases)
Fase 1 – Definició i disseny (1-2 setmanes)
Definir funcionalitats mínimes viables (MVP).
Crear maquetes de la UI (Figma / dibuix simple).
Dissenyar l’estructura de la base de dades.
Fase 2 – Frontend inicial (2-3 setmanes)
Crear app React amb:
Navbar i rutes bàsiques (Identificar, Diccionari, Zones, Historial).
Formulari pujada de fotos.
Pantalla de diccionari (dades mockades).
Fase 3 – Backend bàsic (2-3 setmanes)
API REST amb Express:
/api/identify → rep imatge i retorna resultat dummy.
/api/mushrooms → llista de bolets (mock).
/api/zones/:id → retorna bolets típics de zona.
Fase 4 – IA i dades reals (3-5 setmanes)
Integrar API de reconeixement de bolets o entrenar model simple.
Crear base de dades inicial amb 20-30 bolets típics de Catalunya.
Enllaçar dades reals al frontend.

#### Fase 5 – Funcions avançades (2-3 setmanes)
Historial d’usuari amb login.
Geolocalització automàtica.
Filtrat avançat per temporada, comestible/tòxic.

#### Fase 6 – Proves i desplegament (2 setmanes)
Proves amb usuaris reals (beta).
Desplegar al núvol (Vercel pel frontend, Render/Heroku pel backend).
📦 Producte mínim viable (MVP)
El primer llançament hauria de tenir:
Pujar imatge i rebre predicció dummy (mock).
Diccionari de bolets amb 10-15 espècies.
Secció de zones amb dades predefinides (Montseny, Pirineus).

## 🚀 Futur (possible evolució)
Mapa interactiu amb Leaflet/Mapbox.
Comunitat d’usuaris amb fotos compartides.
Recomanacions personalitzades segons l’historial.
Afegir idiomes

## Fonts, inspiració, codi, dades 
https://www.kaggle.com/datasets/zlatan599/mushroom1
https://www.kaggle.com/code/chitradas/mushroom-species-high-quality-inference/notebook
https://www.researchgate.net/publication/355114369_Mushroom_Image_Classification_with_CNNs_A_Case-Study_of_Different_Learning_Strategies


## UI 


<img width="714" height="709" alt="Captura de Pantalla 2025-10-13 a les 14 22 57" src="https://github.com/user-attachments/assets/1046d02c-d4e0-48dc-a829-e30610ef591c" />

<img width="735" height="1070" alt="Captura de Pantalla 2025-10-13 a les 14 23 56" src="https://github.com/user-attachments/assets/81fcdac4-f4c3-4ff2-885c-b3f2476bd0ef" />

<img width="783" height="991" alt="image" src="https://github.com/user-attachments/assets/82c2d7cc-f0b9-4fbb-b33f-d5653fecdb1a" />


<img width="707" height="827" alt="Captura de Pantalla 2025-10-13 a les 14 23 48" src="https://github.com/user-attachments/assets/a50de3cf-4849-4c8b-ba08-53dca327d067" />

