# HC-1 en HC-2 context

Dit bestand helpt om de game expliciet te koppelen aan de hoorcolleges over neurale netwerken.

## HC-1: wat is een neuraal netwerk?

In HC-1 wordt een neuraal netwerk beschreven als een machine-learningmodel dat input-data verwerkt via berekeningen en daarna output geeft, vaak in de vorm van een voorspelling. In deze game is dat:

- input: de huidige game-state;
- verwerking: hidden layers met gewichten en activatiefuncties;
- output: de actie van de speler.

De AI neemt dus de plek in van de human player.

## Mapping van X naar Y

HC-1 legt uit dat een neuraal netwerk na training kan werken als een functiebenaderaar: het leert een mapping van input `X` naar output `Y`.

In dit project:

- `X` = feature-vector van de game-state;
- `Y` = actie die de speler koos: `-1`, `0` of `1`;
- de geleerde functie voorspelt: `actie = f(game_state)`.

Voorbeeld:

```text
[player_x, stone_x, stone_y, dx, danger_center] -> rechts
```

## Input layer

HC-2 benadrukt dat een input-record als geheel aan een netwerk wordt gegeven. Daarom gebruikt dit project geen volledig screenshot, maar een compacte kenmerkvector:

- `player_x_norm`
- `player_velocity_norm`
- `stone_x_norm`
- `stone_y_norm`
- `stone_speed_norm`
- `dx_norm`
- `abs_dx_norm`
- `danger_left`
- `danger_center`
- `danger_right`

Dit is sneller en conceptueel duidelijker dan werken met duizenden pixels.

## Schalen van input

HC-2 noemt dat neural networks beter presteren wanneer inputwaarden geschaald zijn. Daarom zijn posities en snelheden genormaliseerd naar ongeveer `0..1` of `-1..1`.

Voorbeelden:

- `player_x_norm = player_x / schermbreedte`
- `stone_y_norm = stone_y / schermhoogte`
- `dx_norm = afstand_tussen_steen_en_speler / schermbreedte`

## Connecties, gewichten en trainen

HC-1 behandelt connecties met gewichten. Tijdens training worden deze gewichten aangepast zodat de error lager wordt. In deze opdracht gebeurt dat in `MLPClassifier`:

- eerst zijn de gewichten willekeurig;
- het netwerk voorspelt acties op trainingsdata;
- de fout tussen voorspelde en echte actie wordt berekend;
- de gewichten worden aangepast;
- dit herhaalt voor meerdere epochs/iteraties.

## Hidden layers en architectuur

HC-2 bespreekt architectuurkeuzes:

- aantal input nodes;
- aantal hidden layers;
- aantal nodes per hidden layer;
- output nodes.

In dit project heeft de input layer 10 features. De experimenten testen onder andere:

- 1 hidden layer: `(8,)`, `(16,)`, `(32,)`
- 2 hidden layers: `(16, 8)`, `(32, 16)`
- 3 hidden layers: `(32, 16, 8)`

Dit past bij het idee uit HC-2 dat je via trial and error onderzoekt welke architectuur het beste werkt.

## Activatiefunctie

HC-1 behandelt activatiefuncties zoals ReLU. In `train_model.py` gebruikt het netwerk:

```python
activation="relu"
```

ReLU is rekenkundig eenvoudig en werkt goed voor veel hidden layers.

## Train/test en overfitting

De opdracht vraagt om resultaten te vergelijken. `train_model.py` splitst data in train en test. Als de train-score hoog is maar de test-score veel lager, dan leert het netwerk mogelijk te veel specifieke voorbeelden uit het hoofd. Dat is overfitting.

Daarom logt het script:

- train accuracy;
- test accuracy;
- train F1;
- test F1;
- loss;
- aantal iteraties.

## CPU-performance en twee lagen in de game

De opdracht waarschuwt dat PyGame op een CPU draait en dat TensorFlow-achtige berekeningen langzaam kunnen worden als je te veel pixels verwerkt.

Deze game gebruikt daarom twee lagen:

1. Visuele laag: PyGame tekent speler, stenen en achtergrond.
2. Logische laag: het netwerk ziet alleen een compacte feature-vector.

De AI beslist dus niet op basis van alle pixels, maar op basis van de abstracte toestand van de wereld.
