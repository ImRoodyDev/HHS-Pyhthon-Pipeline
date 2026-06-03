# Practicum 3 - Neural Networks

Deze map bevat de uitwerking voor week 11, practicum 3.

## Bestanden

- `Practicum_3_Neural_Networks_AmesHousing.ipynb`: notebook met alle code voor data laden, feature-sets, linear regression baseline, neural-network experimenten, visualisaties en Excel-export.
- `AmesHousing.xlsx`: lokale kopie van de dataset.
- `experiment_log.xlsx`: Excel-logboektemplate. Na het draaien van de notebook wordt dit bestand gevuld met de resultaten.
- `CODE_EXPLANATION.md`: uitgebreide uitleg van de notebook, HC-termen en alle gebruikte hyperparameters.

## Hoe de code is opgebouwd

De notebook volgt dezelfde stijl als de eerdere practica:

1. Eerst worden feature-sets en hyperparameters in lijsten gezet.
2. Daarna loopt een `for`-loop over alle combinaties.
3. Per experiment worden model, instellingen en scores opgeslagen in een dictionary.
4. Alle dictionaries worden samengevoegd in een `DataFrame`.
5. De resultaten worden vergeleken, geplot en naar Excel geschreven.

Hierdoor hoef je geen losse codeblokken te kopieren voor elke nieuwe test. Een extra experiment toevoegen betekent meestal alleen een extra item toevoegen aan `feature_sets` of `nn_settings`.

## Wat is een neural network?

Een neural network bestaat uit lagen met neurons. Elke neuron maakt een gewogen combinatie van inputwaarden en stuurt die door een activatiefunctie, zoals ReLU. Bij regressie, zoals huizenprijzen voorspellen, leert het netwerk patronen tussen features en de doelvariabele `SalePrice`.

Belangrijke instellingen in deze opdracht:

- `hidden_layers`: aantal hidden layers en aantal neurons per layer. `(64, 32)` betekent twee hidden layers.
- `learning_rate`: hoe groot de aanpassing van de gewichten per stap is.
- `epochs`: hoe vaak het model door de trainingsdata gaat.
- `validation_size`: deel van de trainingsdata dat apart wordt gehouden om instellingen te vergelijken.

Een groter netwerk is niet automatisch beter. Het kan beter patronen leren, maar ook sneller overfitten. Daarom vergelijkt de notebook train-, validation- en test-scores.

## Resultaten beoordelen

Gebruik de validation score om een model te kiezen. Bekijk daarna de test score als laatste controle.

Belangrijke metrics:

- `MAE`: gemiddelde absolute fout in dollars.
- `RMSE`: straft grote fouten zwaarder; lager is beter.
- `R2`: verklaarde variantie; dichter bij 1 is beter.

Vergelijk vooral:

- beste NN per feature-set;
- `all_features` versus kleinere subsets;
- beste NN versus linear regression baseline;
- effect van learning rate, epochs en aantal hidden layers.
