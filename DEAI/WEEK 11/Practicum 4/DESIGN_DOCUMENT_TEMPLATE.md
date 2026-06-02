# Design Document - Practicum 4

Let op: de opdracht zegt dat het design zonder AI moet worden bedacht. Gebruik dit document daarom als invulstructuur en pas alle ontwerpkeuzes aan naar je eigen idee.

## 1. Gameconcept

Naam van de game:

Korte beschrijving:

Wat ziet de speler op het scherm?

Wat is het doel van het spel?

Wanneer is de speler af?

Welke sfeer/stijl wil ik gebruiken?

## 2. Requirements

Functionele requirements:

- De speler kan naar links en rechts bewegen.
- Stenen vallen van boven naar beneden.
- Botsing tussen speler en steen betekent game over.
- De score stijgt wanneer een steen wordt ontweken.
- Tijdens human play wordt trainingsdata opgeslagen.
- Na training kan een neural network de speler besturen.

Eigen extra requirements:

- ...
- ...
- ...

Niet-functionele requirements:

- De game moet soepel draaien op een normale CPU.
- De AI-input gebruikt een compacte feature-vector in plaats van alle pixels.
- Data en resultaten moeten in tabellen/grafieken terug te vinden zijn.

## 3. Game ontwerp

Schermgrootte:

Speler:

- vorm:
- kleur:
- snelheid:
- startpositie:

Stenen:

- vorm:
- kleur:
- snelheid:
- spawn-frequentie:
- worden ze sneller na verloop van tijd?

Score:

- hoe wordt score berekend?
- wordt moeilijkheid langzaam hoger?

## 4. Neural-network ontwerp

Wat neemt het neural network over van de human player?

Welke input-features gebruik ik?

| Feature | Betekenis | Waarom relevant? |
|---|---|---|
| `player_x_norm` | positie van speler | netwerk moet weten waar het blokje staat |
| `stone_x_norm` | positie van steen | netwerk moet weten waar gevaar valt |
| `dx_norm` | afstand steen-speler | bepaalt of ontwijken nodig is |
| ... | ... | ... |

Welke output voorspelt het netwerk?

- `-1`: links
- `0`: blijven staan
- `1`: rechts

Waarom is dit classificatie en geen regressie?

## 5. Trainingsdata

Hoe verzamel ik data?

Welke kolommen worden opgeslagen?

Hoe zorg ik dat de dataset gevarieerd is?

Hoeveel minuten wil ik spelen voordat ik train?

Welke problemen kunnen ontstaan in de dataset?

- te weinig voorbeelden van links/rechts;
- te veel stilstaan;
- te weinig moeilijke situaties;
- data van slechte speelrondes.

## 6. Architecturen en experimenten

Welke architecturen test ik?

| Experiment | Hidden layers | Learning rate | Datasetgrootte | Verwachting |
|---|---:|---:|---:|---|
| 1 | `(8,)` | `0.001` | `25%` | snel, maar mogelijk te simpel |
| 2 | `(16, 8)` | `0.001` | `100%` | goede balans |
| 3 | `(32, 16, 8)` | `0.001` | `100%` | krachtiger, kans op overfitting |

Welke metrics gebruik ik?

- train accuracy;
- test accuracy;
- train F1;
- test F1;
- confusion matrix;
- prestatie in de game.

## 7. Link met HC-1 en HC-2

Gebruik in je eigen woorden:

- Een NN verwerkt input en maakt een voorspelling.
- De game-state is een input-vector.
- Het netwerk leert een mapping van `X` naar `Y`.
- Hidden layers leren patronen in de data.
- ReLU wordt gebruikt als activatiefunctie.
- Tijdens training worden gewichten aangepast om de fout te verlagen.
- Input schalen helpt bij stabiel trainen.
- Te lang of te complex trainen kan overfitting geven.
- Door niet alle pixels te gebruiken blijft de game sneller op CPU.

## 8. Verwachte resultaten

Welke feature-set/architectuur verwacht ik dat goed werkt?

Waarom?

Waar verwacht ik dat de AI nog fouten maakt?

Hoe kan ik het model verbeteren?

## 9. Reflectie na experimenten

Beste experiment:

Train/test verschil:

Gedrag van de AI in de game:

Wat ging goed?

Wat zou ik verbeteren?
