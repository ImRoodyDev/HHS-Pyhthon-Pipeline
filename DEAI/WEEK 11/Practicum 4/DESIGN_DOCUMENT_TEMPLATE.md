# Design Document - Practicum 4

## 1. Gameconcept

Naam van de game: AI Stone Dodger

Korte beschrijving: Een speler beweegt links/rechts onderin het scherm om vallende stenen te ontwijken.

Wat ziet de speler op het scherm? Een donker scherm met een blauw blokje onderaan en rode cirkels die van boven naar beneden vallen.

Wat is het doel van het spel? Zo lang mogelijk overleven. Elke ontweken steen geeft +1 score.

Wanneer is de speler af? Wanneer een steen het blokje raakt.

Welke sfeer/stijl wil ik gebruiken? Minimalistisch en donker met een subtiel raster op de achtergrond.

---

## 2. Requirements

Functionele requirements:

- De speler kan naar links en rechts bewegen met A/D of pijltjestoetsen.
- Stenen vallen van boven naar beneden op willekeurige posities.
- Botsing tussen speler en steen betekent game over.
- De score stijgt wanneer een steen wordt ontweken.
- Tijdens human play wordt trainingsdata opgeslagen in een CSV-bestand.
- Na training kan een neural network de speler besturen.

Eigen extra requirements:

- Een heuristic-modus als snelle demo zonder getraind model.
- De score wordt live op het scherm getoond.
- Bij game over verschijnt een overlay met de optie om opnieuw te starten.

Niet-functionele requirements:

- De game moet soepel draaien op een normale CPU.
- De AI-input gebruikt een compacte feature-vector in plaats van alle pixels.
- Data en resultaten moeten in tabellen/grafieken terug te vinden zijn.

---

## 3. Game ontwerp

Schermgrootte: 640 × 480 pixels, 60 FPS

Speler:

- vorm: rechthoek (44 × 30 px)
- kleur: blauw met lichtblauwe rand
- snelheid: 360 px/s
- startpositie: horizontaal gecentreerd, onderaan het scherm

Stenen:

- vorm: cirkel met willekeurige straal (14–24 px)
- kleur: rood met lichte highlight
- snelheid: willekeurig tussen 170 en 285 px/s per steen
- spawn-frequentie: elke 0.55 seconden op een willekeurige X-positie
- worden ze sneller na verloop van tijd? Nee, de variatie zit al in de willekeurige snelheid per steen.

Score:

- hoe wordt score berekend? +1 per steen die de onderkant verlaat zonder de speler te raken.
- wordt moeilijkheid langzaam hoger? Nee.

---

## 4. Neural-network ontwerp

Wat neemt het neural network over van de human player? Het netwerk beslist elke frame of de speler links, rechts of stilstaat op basis van de huidige spelstaat.

Welke input-features gebruik ik?

| Feature                | Betekenis                          | Waarom relevant?                         |
| ---------------------- | ---------------------------------- | ---------------------------------------- |
| `player_x_norm`        | positie van speler                 | netwerk moet weten waar het blokje staat |
| `player_velocity_norm` | huidige bewegingssnelheid          | weet of het blokje al beweegt            |
| `stone_x_norm`         | positie van dichtstbijzijnde steen | netwerk moet weten waar gevaar valt      |
| `stone_y_norm`         | hoogte van die steen               | hoe dichtbij is het gevaar               |
| `stone_speed_norm`     | valsnelheid van die steen          | snellere stenen vragen eerder reactie    |
| `dx_norm`              | horizontale afstand steen−speler   | bepaalt of ontwijken nodig is            |
| `abs_dx_norm`          | absolute waarde van dx             | makkelijk te gebruiken drempelfeature    |
| `danger_left`          | gevaar bij links bewegen?          | vertelt of links veilig is               |
| `danger_center`        | gevaar bij stilstaan?              | vertelt of stilstaan veilig is           |
| `danger_right`         | gevaar bij rechts bewegen?         | vertelt of rechts veilig is              |

Welke output voorspelt het netwerk?

- `-1`: links
- `0`: blijven staan
- `1`: rechts

Waarom is dit classificatie en geen regressie? De actieruimte bestaat uit drie vaste keuzes. Een tussenwaarde zoals `0.4` heeft geen betekenis in de game; het netwerk moet één van de drie acties kiezen.

---

## 5. Trainingsdata

Hoe verzamel ik data? Door het spel te spelen in human-modus. Elke frame wordt automatisch opgeslagen als rij in `data/training_data.csv`.

Welke kolommen worden opgeslagen? `timestamp`, `score`, de 10 features uit sectie 4, en `action` (−1/0/1).

Hoe zorg ik dat de dataset gevarieerd is? Meerdere rondes spelen, bewust naar links én rechts bewegen, en ook rondes meenemen waarbij het bijna misgaat.

Hoeveel minuten wil ik spelen voordat ik train? Minimaal 5–10 minuten (~18.000–36.000 rijen bij 60 FPS).

Welke problemen kunnen ontstaan in de dataset?

- te weinig voorbeelden van links/rechts;
- te veel stilstaan;
- te weinig moeilijke situaties;
- data van slechte speelrondes.

---

## 6. Architecturen en experimenten

Welke architecturen test ik?

| Experiment | Hidden layers | Learning rate | Datasetgrootte | Verwachting                                  |
| ---------- | ------------: | ------------: | -------------: | -------------------------------------------- |
| 1          |        `(8,)` |       `0.001` |         `100%` | snel, maar mogelijk te simpel                |
| 2          |     `(16, 8)` |       `0.001` |         `100%` | goede balans                                 |
| 3          |    `(32, 16)` |       `0.001` |         `100%` | meer capaciteit, kans op overfitting         |
| 4          | `(32, 16, 8)` |       `0.001` |         `100%` | dieper netwerk, test of extra laag helpt     |
| 5          |     `(16, 8)` |        `0.01` |         `100%` | hogere learning rate, minder stabiel?        |
| 6          |     `(16, 8)` |      `0.0001` |         `100%` | lagere learning rate, trager maar stabieler? |

Welke metrics gebruik ik?

- train accuracy;
- test accuracy;
- train F1;
- test F1;
- confusion matrix;
- prestatie in de game.

---

## 7. Link met HC-1 en HC-2

Gebruik in je eigen woorden:

- Een NN verwerkt input en maakt een voorspelling: het netwerk krijgt 10 waarden over de spelstaat en geeft een actie terug.
- De game-state is een input-vector: alle relevante informatie over speler en steen wordt als één rij getallen aangeboden.
- Het netwerk leert een mapping van `X` naar `Y`: van spelstaat naar actie, door te kijken naar hoe ik zelf speelde.
- Hidden layers leren patronen in de data: de eerste laag herkent misschien gevaar, de tweede laag besluit welke kant op.
- ReLU wordt gebruikt als activatiefunctie: neuronen geven alleen een signaal door als de waarde positief is.
- Tijdens training worden gewichten aangepast om de fout te verlagen: het netwerk vergelijkt zijn voorspelling met mijn actie en past zich aan.
- Input schalen helpt bij stabiel trainen: alle features liggen tussen −1 en 1 zodat geen enkele feature domineert.
- Te lang of te complex trainen kan overfitting geven: het model onthoudt dan de trainingsdata in plaats van te generaliseren.
- Door niet alle pixels te gebruiken blijft de game sneller op CPU: 10 features zijn veel efficiënter dan 307.200 pixelwaarden.

---

## 8. Verwachte resultaten

Welke feature-set/architectuur verwacht ik dat goed werkt? Experiment 2: `(16, 8)` met learning rate `0.001`.

Waarom? Genoeg capaciteit voor het patroon, maar niet zo groot dat overfitting snel optreedt.

Waar verwacht ik dat de AI nog fouten maakt? Bij meerdere stenen tegelijk en bij stenen met een hoge valsnelheid die laat worden gespot.

Hoe kan ik het model verbeteren? Meer trainingsdata verzamelen en de klassen balanceren zodat links/rechts/stilstaan even vaak voorkomen.

---

## 9. Reflectie na experimenten

_(In te vullen na het draaien van de experimenten)_

Beste experiment:

Train/test verschil:

Gedrag van de AI in de game:

Wat ging goed?

Wat zou ik verbeteren?
