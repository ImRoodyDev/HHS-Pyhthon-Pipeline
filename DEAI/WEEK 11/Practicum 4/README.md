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
