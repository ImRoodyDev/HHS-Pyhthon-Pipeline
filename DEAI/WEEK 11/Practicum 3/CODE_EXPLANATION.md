# Practicum 3 - Code Explanation and Hyperparameters

This file explains the notebook `Practicum_3_Neural_Networks_AmesHousing.ipynb`.
It uses terms from HC-1 and HC-2:

- input-record / kenmerkvector
- input layer
- hidden layer
- output layer
- connecties and gewichten
- activatiefunctie `h()`
- training, error and loss
- mapping from `X` to `Y`
- feature scaling
- overfitting and generalisation

## 1. What the assignment does

The goal is to predict `SalePrice` from the AmesHousing dataset.

In HC-1 a neural network is explained as a model that receives input data,
does calculations through layers, and produces an output. In this practicum:

- `X` is a row from the housing dataset.
- `X` is the input-record / kenmerkvector.
- `Y` is `SalePrice`.
- The neural network learns the mapping `X -> SalePrice`.

So the model behaves like a function approximator:

```text
house features -> predicted house price
```

This is a regression task because the output is a continuous number, not a class.

## 2. Main files

| File | Role |
|---|---|
| `Practicum_3_Neural_Networks_AmesHousing.ipynb` | Main notebook with all experiments |
| `AmesHousing.xlsx` | Dataset copied into the practicum folder |
| `experiment_log.xlsx` | Excel output/logbook for experiment results |
| `README.md` | Short project overview |
| `CODE_EXPLANATION.md` | This detailed explanation |

## 3. Notebook structure

The notebook is built in this order:

1. Import libraries.
2. Load `AmesHousing.xlsx`.
3. Detect numeric and categorical columns.
4. Define multiple feature-sets.
5. Build helper functions for preprocessing, splitting and metrics.
6. Train a LinearRegression baseline.
7. Define neural-network settings.
8. Loop over every feature-set and NN setting.
9. Store metrics in a results list.
10. Convert results to DataFrames.
11. Compare validation/test scores.
12. Plot best results.
13. Export results to Excel.

This follows the same style as earlier practica: define configurations once,
then use loops to avoid copy-paste.

## 4. Imports explained

The important imports are:

| Import | Why it is used |
|---|---|
| `pandas` | Read Excel data and create result tables |
| `numpy` | Numeric calculations, for example RMSE |
| `matplotlib` | Graphs for comparisons and predictions |
| `train_test_split` | Split data into train, validation and test |
| `LinearRegression` | Baseline model from earlier ML work |
| `MLPRegressor` | Neural network for regression |
| `Pipeline` | Combine preprocessing and model in one object |
| `ColumnTransformer` | Apply different preprocessing to numeric/categorical columns |
| `SimpleImputer` | Fill missing values |
| `StandardScaler` | Scale numeric values |
| `OneHotEncoder` | Convert categorical text to numeric columns |
| `TransformedTargetRegressor` | Scale the target `SalePrice` for NN training |

## 5. Data loading

The notebook loads:

```python
df = pd.read_excel(DATA_FILE)
```

`DATA_FILE` points to `AmesHousing.xlsx`.

The target is:

```python
TARGET = "SalePrice"
```

`ID` is not used as feature because it is just an identifier. It does not
describe a house.

## 6. Feature-sets

The notebook defines several `feature_sets`.

Each feature-set is one possible input-vector design. This is a direct link
to HC-2: an input-record consists of multiple input values.

Current feature-sets:

| Feature-set | Meaning |
|---|---|
| `week6_neighborhood_basic` | Small set similar to previous linear regression work |
| `week6_house_style_basic` | Small set with house style |
| `quality_living_basement` | Strong numeric house-quality/size features |
| `size_age_rooms` | Numeric features about size, year and rooms |
| `all_numeric` | All numeric columns except `ID` and `SalePrice` |
| `all_features` | Numeric + categorical columns |

Why this matters:

- A smaller input-vector can train faster and overfit less.
- A larger input-vector gives the model more information.
- More features are not automatically better.
- The experiment answers whether all features or a subset works best.

## 7. Preprocessing pipeline

The function `build_preprocessor(X)` prepares the input data before training.

### Numeric columns

Numeric columns go through:

```python
SimpleImputer(strategy="median")
StandardScaler()
```

Effect:

- Missing values are filled with the median.
- Values are scaled to similar ranges.

This follows HC-2: neural networks perform better when input data is scaled.
For example, a feature with values around 200000 should not dominate a feature
with values around 2.

### Categorical columns

Categorical columns go through:

```python
SimpleImputer(strategy="most_frequent")
OneHotEncoder(handle_unknown="ignore")
```

Effect:

- Missing text values are filled.
- Text categories become numeric 0/1 columns.

For example:

```text
Neighborhood = "NAmes"
```

becomes something like:

```text
Neighborhood_NAmes = 1
Neighborhood_OldTown = 0
...
```

The network cannot process text directly, so this conversion is necessary.

## 8. Train, validation and test split

The notebook uses:

```python
make_train_validation_test_split(X, y, validation_size, test_size=0.15)
```

The split is:

- test set: final check, fixed at 15 percent of all data.
- validation set: used to compare hyperparameters.
- train set: used to update the weights.

Why this matters:

- Train score tells how well the model learned the training examples.
- Validation score helps choose the best settings.
- Test score tells how well the chosen model generalises to unseen data.

This connects to HC-2 overfitting: if train is good but validation/test is bad,
the model learned the training data too specifically.

## 9. Metrics

The notebook calculates:

| Metric | Meaning | Better |
|---|---|---|
| `MAE` | Average absolute error in house price | Lower |
| `MSE` | Average squared error | Lower |
| `RMSE` | Square root of MSE, in house-price units | Lower |
| `R2` | Explained variance | Higher |

For this assignment, `RMSE` is useful because it is still in the same unit as
`SalePrice`, but it punishes large errors more strongly than MAE.

## 10. LinearRegression baseline

Before training neural networks, the notebook trains:

```python
LinearRegression()
```

This is the baseline from earlier ML work.

Why baseline is important:

- It shows whether the neural network actually improves performance.
- If LinearRegression is already better, the NN might be unnecessary.
- It gives a fair comparison per feature-set.

## 11. Neural network model

The function:

```python
build_nn_model(...)
```

creates a full model:

```text
preprocessing -> MLPRegressor -> target scaling wrapper
```

### Why `MLPRegressor`?

`MLPRegressor` is a feed-forward neural network for regression.

In HC terms:

- input layer: processed feature-vector.
- hidden layers: configured by `hidden_layers`.
- connecties: learned weights between nodes.
- activatiefunctie `h()`: ReLU.
- output layer: one numeric value, predicted `SalePrice`.

## 12. Why target scaling is used

The notebook wraps the model in:

```python
TransformedTargetRegressor(transformer=StandardScaler())
```

This scales `SalePrice` during training.

Reason:

- House prices are large numbers.
- Neural networks often train more stable when both input and target are scaled.
- The wrapper automatically converts predictions back to original house-price units.

## 13. Experiment loop

The experiment loop has two levels:

```python
for feature_set in feature_sets:
    for setting in nn_settings:
        train model
        predict
        calculate metrics
        store result row
```

This creates:

```text
6 feature-sets * 10 NN settings = 60 NN experiments
```

Each row stores:

- feature-set name
- hidden layers
- learning rate
- epochs
- validation size
- train/validation/test rows
- train/validation/test metrics
- final training loss
- actual iterations

## 14. Hyperparameters in Practicum 3

Hyperparameters are choices made before training. The network learns weights,
but it does not choose these settings by itself.

### `hidden_layers`

Example values:

```python
(16,)
(64, 32)
(128, 64, 32)
```

Meaning:

- `(16,)` means 1 hidden layer with 16 nodes.
- `(64, 32)` means 2 hidden layers: first 64 nodes, then 32 nodes.
- `(128, 64, 32)` means 3 hidden layers.

Effect:

- More hidden layers/nodes means more connecties and weights.
- More capacity can learn more complex mappings.
- More capacity also increases training time and overfitting risk.

HC-2 link: architecture can vary in number of input nodes, output nodes, hidden
layers and nodes per hidden layer.

### `hidden_layer_count`

This is not directly passed to sklearn. It is logged for analysis.

Effect:

- Helps compare 1, 2 and 3 hidden layers.
- Useful for answering the assignment question about different architectures.

### `hidden_nodes_total`

This is also a logging field.

Effect:

- Gives a quick idea of model size.
- More total nodes usually means more weights.
- More weights means more memory, more CPU work and more overfitting risk.

HC-2 link: large networks have many connecties, which affects memory and
processing.

### `learning_rate`

Used as:

```python
learning_rate_init=learning_rate
```

Tested values:

```python
0.0001
0.0005
0.001
0.01
```

Effect:

- Low learning rate: small weight updates, stable but slow.
- High learning rate: faster updates, but can overshoot good solutions.
- Too high can make loss unstable.
- Too low may need many epochs.

HC link: training adjusts connectiegewichten based on error. The learning rate
controls how large those adjustments are.

### `epochs`

Used as:

```python
max_iter=epochs
```

Tested values:

```python
80
120
160
200
```

Meaning:

- One epoch means the model has gone through the training data once.
- In sklearn `MLPRegressor`, `max_iter` is the maximum number of training
  iterations.

Effect:

- Too few epochs: underfitting. Model has not learned enough.
- Too many epochs: overfitting risk. Model may memorise training data.
- More epochs also means longer runtime.

HC link: training repeats until error is low enough or a stop criterion is met.

### `validation_size`

Tested values:

```python
0.15
0.20
0.30
```

Meaning:

- From the train/validation part, this fraction becomes validation data.
- The test set remains fixed at 15 percent.

Effect:

- Larger validation set gives a more reliable validation score.
- Larger validation set leaves less data for training.
- Smaller validation set gives more training data but noisier validation results.

### `batch_size`

Used as:

```python
batch_size=32
```

Meaning:

- The model updates weights after processing batches of 32 rows.

Effect:

- Smaller batch: noisier updates, sometimes generalises better, slower.
- Larger batch: smoother updates, faster per epoch, may generalise worse.
- `32` is a common practical default.

### `alpha`

Used as:

```python
alpha=0.0001
```

Meaning:

- L2 regularisation.
- It adds a penalty for very large weights.

Effect:

- Higher alpha: simpler model, less overfitting, possible underfitting.
- Lower alpha: more freedom, possibly better train score, more overfitting risk.

### `activation`

Used as:

```python
activation="relu"
```

Meaning:

- ReLU is the activatiefunctie `h()`.
- ReLU returns 0 for negative input and keeps positive input.

Effect:

- Adds non-linearity.
- Without a non-linear activation, extra layers behave too much like a linear
  model.
- ReLU is computationally simple.

HC-1 link: activation functions are needed so the network can learn non-linear
patterns.

### `solver`

Used as:

```python
solver="adam"
```

Meaning:

- Adam is the training algorithm that updates the weights.

Effect:

- Usually works well without much manual tuning.
- Adapts update sizes per weight.

HC link: the training algorithm uses error to adjust connectiegewichten.

### `early_stopping`

Used as:

```python
early_stopping=False
```

Meaning:

- The model does not automatically stop early based on internal validation.

Effect:

- Experiments are easier to compare because `epochs` stays the planned limit.
- But it can train longer than necessary.

### `random_state`

Used as:

```python
random_state=42
```

Effect:

- Makes train/test splits and neural-network initial weights reproducible.
- Same code should give similar results each run.

## 15. How to read the results

Use validation score to choose a model.

Then check test score.

Good signs:

- low validation RMSE
- low test RMSE
- high validation/test R2
- train and validation scores are close

Warning signs:

- train score much better than validation/test: overfitting
- train and validation both bad: underfitting
- loss is still dropping at the end: maybe more epochs needed
- loss is unstable: learning rate may be too high

## 16. What to write in the conclusion

Answer these questions:

1. Which feature-set had the best validation RMSE?
2. Did `all_features` beat smaller feature-sets?
3. Did the NN beat LinearRegression?
4. Which learning rate worked best?
5. Did 1, 2 or 3 hidden layers work best?
6. Was there overfitting?
7. What would you test next?

