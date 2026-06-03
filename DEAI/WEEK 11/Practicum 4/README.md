# Practicum 4 - AI Stone Dodger

Dit project bouwt een eenvoudige 2D-game waarin een speler vallende stenen ontwijkt. Tijdens human play wordt trainingsdata opgeslagen. Daarna train je een neuraal netwerk dat de speler vervangt.

## Bestanden

- `game.py`: PyGame-game met drie modi: human, heuristic en AI.
- `train_model.py`: traint meerdere neural-network experimenten en slaat het beste model op.
- `requirements.txt`: benodigde packages.
- `DESIGN_DOCUMENT_TEMPLATE.md`: invulbaar design document. Vul dit zelf aan, omdat de opdracht aangeeft dat het design zonder AI moet worden bedacht.
- `HC_CONTEXT.md`: koppeling tussen de game en begrippen uit HC-1 en HC-2.
- `data/`: hier komt `training_data.csv`.
- `models/`: hier komt `best_model.joblib`.
- `logs/`: hier komen experimenttabellen en grafieken.

## Installatie

```powershell
pip install -r requirements.txt
```

## Fase 1: design document

Open `DESIGN_DOCUMENT_TEMPLATE.md` en vul je eigen keuzes in:

- hoe het spel eruitziet;
- welke game-state de input-vector vormt;
- waarom de output `links`, `blijven` of `rechts` is;
- welke visuals of extra regels jij toevoegt;
- welke experimenten je wilt draaien.

Gebruik `HC_CONTEXT.md` om begrippen uit de hoorcolleges bewust te verwerken.

## Fase 2: game spelen en data verzamelen

Speel zelf en verzamel data:

```powershell
python game.py --mode human --record data/training_data.csv
```

Besturing:

- `A` of pijl links: naar links
- `D` of pijl rechts: naar rechts
- geen toets: blijven staan
- `Q`: stoppen

Probeer gevarieerd te spelen. Het model leert alleen van wat jij voordoet. Als je bijna nooit stilstaat of nooit naar links beweegt, krijgt het netwerk een scheve dataset.

## Fase 3: neural network trainen

Train meerdere architecturen en datasetgroottes:

```powershell
python train_model.py --data data/training_data.csv
```

De training maakt:

- `logs/experiment_results.csv`
- `logs/experiment_results.xlsx`
- `logs/experiment_accuracy.png`
- `logs/best_confusion_matrix.png`
- `logs/best_classification_report.txt`
- `models/best_model.joblib`

## AI laten spelen

```powershell
python game.py --mode ai --model models/best_model.joblib
```

## Experimenten

`train_model.py` test:

- 1 hidden layer: `(8,)`, `(16,)`, `(32,)`
- 2 hidden layers: `(16, 8)`, `(32, 16)`
- 3 hidden layers: `(32, 16, 8)`
- learning rates: `0.0005`, `0.001`, `0.01`
- datasetgroottes: `25%`, `50%`, `100%`

De belangrijkste vergelijking is train-score versus test-score. Als train veel hoger is dan test, kan het model overfitten.

## Waarom geen pixels als input?

PyGame tekent in pixels, maar het neural network gebruikt niet het volledige scherm als input. In plaats daarvan krijgt het model een kleine feature-vector, bijvoorbeeld:

- positie van de speler;
- snelheid/richting van de speler;
- positie en snelheid van de gevaarlijkste steen;
- afstand tussen speler en steen;
- simpele danger-features voor links, midden en rechts.

Dit sluit aan bij HC-2: een input-record is een kenmerkvector. Het is ook sneller dan duizenden pixels per frame door het netwerk sturen.

## Handige workflow

1. Speel 2 tot 5 minuten en verzamel data.
2. Train het model.
3. Laat de AI spelen.
4. Bekijk waar de AI fouten maakt.
5. Verzamel meer data voor die situaties.
6. Train opnieuw en vergelijk de resultaten.

---

## Hoe werkt het neural network? (HC-terminologie)

> De begrippen hieronder komen rechtstreeks uit HC-1 en HC-2 van de cursus.

### Wat het NN in deze opdracht doet

Per frame levert de game een **input-record** (= kenmerkvector, HC-2) aan het netwerk.  
Dat record bevat 10 genormaliseerde getallen: positie van de speler, positie/snelheid van de gevaarlijkste steen, en drie danger-waarden.  
Het netwerk **mapt** die input naar één van drie klassen: `links (-1)`, `blijven (0)` of `rechts (1)`.  
Dit is een **classificatieprobleem** (HC-2), niet regressie — de output is een categorie, geen getal.

Vrij vertaald naar HC-1: het netwerk gedraagt zich als een **universele functiebenaderaar**.  
Na het trainen doet het _alsof het een functie is_ die de game-state (x) vertaalt naar de juiste actie (y).

### Bouwstenen van het NN (HC-1, slides 8, 23–26)

| HC-begrip                 | In de code                                                                |
| ------------------------- | ------------------------------------------------------------------------- |
| **Input layer**           | de 10 waarden in `FEATURE_COLUMNS` (geen echte neuronen, alleen data)     |
| **Hidden layer(s)**       | `hidden_layer_sizes` in `EXPERIMENTS`, bijv. `(32, 16)` = 2 hidden layers |
| **Knoop / neuron / node** | elk getal in een hidden layer; berekent `h(Σ xᵢ · wᵢ + b)`                |
| **Connectie**             | de verbinding tussen twee knopen in opeenvolgende lagen                   |
| **Gewicht (weight)**      | het getal op elke connectie; sklearn past dit aan tijdens het trainen     |
| **Activatiefunctie h()**  | `activation="relu"` — verwijdert negatieve waarden (HC-1, slide 44)       |
| **Output layer**          | één knoop per klasse (`-1`, `0`, `1`); softmax bepaalt de eindklasse      |

### Hoe het trainen werkt (HC-1, slides 35–40)

```
1. Neem één frame-record uit training_data.csv als input
2. Voer de input van links naar rechts door het netwerk
3. Bereken de output (voorspelde actie)
4. Bereken de Error = voorspelde actie − werkelijke actie die de mens deed
5. Pas alle gewichten een klein beetje aan (backpropagation + Adam-optimizer)
6. Herhaal voor alle records → 1 epoch
7. Herhaal voor max_iter epochs
```

sklearn's `MLPClassifier` doet dit automatisch met `model.fit(X_train, y_train)`.  
Het algoritme dat de gewichten aanpast heet **Adam** (`solver="adam"`) — een verbeterde versie van gradient descent.

### Waarom ReLU als activatiefunctie? (HC-1, slide 44)

- ReLU = `max(0, x)` — gooit negatieve waarden weg, laat positieve door.
- Eenvoudig te berekenen (geen exponenten zoals sigmoid of tanh).
- Zorgt voor **niet-lineariteit**: zonder een activatiefunctie kan het netwerk alleen rechte lijnen leren, en dat is te simpel voor een game met meerdere stenen (HC-1, slide 30).

### Waarom de features schalen?

`StandardScaler` zet alle features op gemiddelde 0 en standaarddeviatie 1.  
Zonder schaling krijgen features met grote waarden (bijv. positie in pixels) veel meer invloed dan features met kleine waarden — dat maakt trainen instabiel.  
Dit sluit aan bij HC-2: een kenmerkvector moet numeriek vergelijkbaar zijn voordat je hem aan een NN geeft.

### game.py — kernonderdelen uitgelegd

| Functie                            | Wat het doet                                                               |
| ---------------------------------- | -------------------------------------------------------------------------- |
| `extract_features(player, stones)` | Bouwt de 10-waarden input-vector per frame; dit is de **input layer** data |
| `nearest_dangerous_stone()`        | Kiest de meest bedreigende steen op basis van tijd-tot-aankomst            |
| `danger_for_action()`              | Simuleert de toekomstige positie voor elk van de 3 acties                  |
| `TrainingLogger`                   | Schrijft elk frame naar CSV: features + actie van de mens                  |
| `run_game()`                       | Game loop: dt-gebaseerde physics, spawn timer, botsingsdetectie            |
| `heuristic_action()`               | Simpele rule-based AI (geen NN) — handig om te vergelijken                 |

### train_model.py — kernonderdelen uitgelegd

| Functie               | Wat het doet                                                      |
| --------------------- | ----------------------------------------------------------------- |
| `load_dataset()`      | Laadt CSV, valideert kolommen, controleert klassebalans           |
| `build_model(config)` | Maakt een `Pipeline`: StandardScaler → MLPClassifier              |
| `train_experiments()` | Loopt over 3 dataset-groottes × 8 architecturen = 24 experimenten |
| `save_outputs()`      | Slaat CSV, Excel, grafieken en het beste model op als `.joblib`   |

Het beste model wordt gekozen op **test F1-macro** — dat weegt alle drie de klassen gelijk, ook als de dataset scheef is (veel "blijven", weinig "links").

---

## Hyperparameters en hun effect

Elke hyperparameter is een instelling die je _vóór_ het trainen kiest; het netwerk leert ze niet zelf aan.

### `hidden_layer_sizes` — architectuur van het netwerk

| Waarde        | Lagen           | Totale knopen | Wanneer gebruiken                              |
| ------------- | --------------- | ------------- | ---------------------------------------------- |
| `(8,)`        | 1 hidden layer  | 8             | Zeer eenvoudig patroon, weinig data            |
| `(16,)`       | 1 hidden layer  | 16            | Lichtere variant, sneller te trainen           |
| `(32,)`       | 1 hidden layer  | 32            | Standaard startpunt voor 1 laag                |
| `(16, 8)`     | 2 hidden layers | 24            | Kan complexere patronen leren                  |
| `(32, 16)`    | 2 hidden layers | 48            | Meer capaciteit, kans op overfitting neemt toe |
| `(32, 16, 8)` | 3 hidden layers | 56            | Diepste netwerk — leert abstracte patronen     |

**Effect**: meer knopen/lagen = meer gewichten = het netwerk kan complexere functies leren.  
Maar: meer knopen vereisen meer trainingsdata en trainen langer. Met weinig data gaat een groot netwerk **overfitten** (train-accuracy hoog, test-accuracy laag).

HC-link: slide 16 en 21 — "hoe meer knopen, hoe nauwkeuriger de benadering van y".

---

### `learning_rate_init` — stapgrootte van gewichtsaanpassing

| Waarde   | Effect                                                                     |
| -------- | -------------------------------------------------------------------------- |
| `0.0005` | Kleine stappen — traint langzaam maar stabiel, minder kans op overschieten |
| `0.001`  | Standaardwaarde — goede balans tussen snelheid en stabiliteit              |
| `0.01`   | Grote stappen — traint snel, maar kan oscilleren of divergeren             |

**Effect**: de learning rate bepaalt hoe groot de aanpassing van elk gewicht is per stap (HC-1, slide 38–39: "pas het gewicht een klein beetje aan").

- Te hoog → het netwerk "springt" over de goede oplossing heen, loss daalt niet meer.
- Te laag → het netwerk convergeert wel, maar duurt heel lang; soms blijft het steken in een lokaal minimum.

---

### `max_iter` — maximaal aantal epochs

| Waarde    | Wanneer genoeg                            |
| --------- | ----------------------------------------- |
| `150`     | Kleine architecturen `(8,)` met veel data |
| `200–250` | Gemiddelde architecturen                  |
| `300`     | Grotere architecturen of weinig data      |

**Effect**: één epoch = het netwerk heeft alle trainingsrijen één keer gezien (HC-1, slide 39: "doe dit voor alle records → 1 iteratie").

- Te weinig epochs → **underfitting**: het netwerk heeft niet genoeg geleerd, zowel train als test zijn laag.
- Te veel epochs → **overfitting**: het netwerk heeft de trainingsdata uit het hoofd geleerd maar generaliseert slecht naar nieuwe frames.
- sklearn stopt vroeg als de loss niet meer daalt (`n_iter_ < max_iter` in de output).

---

### `alpha` — L2-regularisatie (gewichtsbestraffing)

Waarde in alle experimenten: `0.0001` (vastgezet).

**Effect**: alpha voegt een straf toe aan grote gewichten. Na elke stap worden de gewichten iets kleiner gemaakt — dit voorkomt dat het netwerk te specifiek leert op de trainingsdata.

- Hoger alpha → zwakkere gewichten → simpeler model → minder overfitting, maar ook minder capaciteit.
- Lager alpha (richting 0) → het netwerk mag grote gewichten hebben → meer capaciteit, meer kans op overfitting.

---

### `dataset_fraction` — hoeveelheid trainingsdata

| Waarde | Rijen (bij ~3000 totaal) | Effect                                    |
| ------ | ------------------------ | ----------------------------------------- |
| `0.25` | ~750                     | Klein — netwerk ziet weinig variatie      |
| `0.50` | ~1500                    | Matig — redelijk beeld van het spelgedrag |
| `1.00` | ~3000                    | Volledig — beste generalisatie            |

**Effect**: meer data = het netwerk leert een breder scala aan situaties.  
Vergelijk train_accuracy vs test_accuracy per fractie: bij 25% zie je vaker een grote kloof (overfitting) dan bij 100%.  
Dit is de HC-2 les over trainingsdata: een model leert alleen van wat het heeft gezien.

---

### Overzicht: wat te verwachten in de resultaten

| Vergelijking                                | Wat je ziet als het klopt                                                                 |
| ------------------------------------------- | ----------------------------------------------------------------------------------------- |
| 1 laag vs 3 lagen                           | 3 lagen heeft hogere train-accuracy, test-accuracy vergelijkbaar of lager bij weinig data |
| learning_rate 0.0005 vs 0.01                | 0.01 convergeert sneller maar is minder stabiel                                           |
| 25% vs 100% data                            | 100% geeft hogere test-accuracy en kleinere kloof train/test                              |
| train-accuracy >> test-accuracy             | Overfitting: model heeft data uit hoofd geleerd, niet de onderliggende patronen           |
| train-accuracy ≈ test-accuracy (beide laag) | Underfitting: model te simpel of te weinig epochs                                         |
