# Practicum 4 - Game Code Explanation

This file explains the code for the PyGame AI game.
It is separate from Practicum 3 because Practicum 4 is about using a neural
network in a game context.

It follows terms from HC-1 and HC-2:

- input-record / kenmerkvector
- input layer
- hidden layer
- output layer
- connecties and weights
- activatiefunctie `h()`
- mapping from input to output
- training, error and loss
- feature scaling
- architecture
- overfitting
- CPU/GPU performance

## 1. What the game does

The game is a small 2D dodging game.

- A player block moves left or right.
- Stones fall from the top of the screen.
- If a stone hits the player, the game ends.
- If a stone leaves the bottom of the screen, the score increases.

The AI part:

1. You play the game yourself in `human` mode.
2. The game saves one CSV row per frame.
3. Each row stores the game-state and your action.
4. `train_model.py` trains a neural network on that CSV.
5. `game.py --mode ai` loads the trained model.
6. The model predicts actions and plays instead of the human.

In HC terms:

```text
game-state input-vector -> neural network -> action
```

## 2. Files

| File | Role |
|---|---|
| `game.py` | Runs the PyGame game, records data, loads AI model |
| `train_model.py` | Trains several `MLPClassifier` experiments |
| `data/training_data.csv` | Gameplay dataset collected from human play |
| `models/best_model.joblib` | Best trained neural-network model |
| `logs/experiment_results.xlsx` | Experiment results |
| `logs/experiment_accuracy.png` | Train/test accuracy graph |
| `logs/best_confusion_matrix.png` | Confusion matrix of the best model |

## 3. Why this is classification

The neural network predicts one of three actions:

| Action | Meaning |
|---|---|
| `-1` | Move left |
| `0` | Stay still |
| `1` | Move right |

This is classification because the output is a class/category.

Practicum 3 is regression because the output is a house price.
Practicum 4 is classification because the output is a movement class.

## 4. Why the AI does not use pixels

HC-2 explains that an input-record is offered to the neural network as a
kenmerkvector. A screenshot could also be an input-vector, but it would contain
many pixels.

This game avoids pixel input for two reasons:

1. CPU performance: PyGame and model prediction run on the CPU.
2. Simplicity: the logical game-state is easier to understand than raw pixels.

So the project uses two layers:

| Layer | Purpose |
|---|---|
| Visual layer | PyGame draws blocks, stones, grid and text |
| Logic/AI layer | Neural network receives 10 numeric features |

This follows the assignment tip: the game can look visual, while the background
world stays simple.

## 5. `game.py` constants

At the top of `game.py` there are constants:

| Constant | Meaning | Effect |
|---|---|---|
| `WIDTH`, `HEIGHT` | Window size in pixels | Larger values mean more space but more drawing |
| `FPS` | Target frames per second | Higher FPS is smoother but uses more CPU |
| `PLAYER_WIDTH`, `PLAYER_HEIGHT` | Player size | Larger player is easier to hit |
| `PLAYER_SPEED` | Movement speed in pixels per second | Higher speed makes dodging easier |
| `STONE_MIN_RADIUS`, `STONE_MAX_RADIUS` | Stone size range | Larger stones are harder to avoid |
| `STONE_MIN_SPEED`, `STONE_MAX_SPEED` | Stone falling speed | Faster stones make the game harder |
| `SPAWN_SECONDS` | Time between new stones | Lower value means more stones and harder game |

These are game parameters, not neural-network hyperparameters.
They still affect the data because changing the game changes the situations the
network learns from.

## 6. Feature columns: the input layer data

`FEATURE_COLUMNS` defines the 10 values used by the neural network:

| Feature | Meaning | Why useful |
|---|---|---|
| `player_x_norm` | Player x-position scaled to 0..1 | The model needs to know where it is |
| `player_velocity_norm` | Current player movement direction/speed | Helps understand current motion |
| `stone_x_norm` | Dangerous stone x-position scaled to 0..1 | Shows where danger is horizontally |
| `stone_y_norm` | Dangerous stone y-position scaled to 0..1 | Shows how close danger is vertically |
| `stone_speed_norm` | Dangerous stone speed scaled | Faster stones require earlier movement |
| `dx_norm` | Signed distance stone minus player | Shows whether danger is left or right |
| `abs_dx_norm` | Absolute distance | Shows how close the danger is |
| `danger_left` | Would moving left be dangerous? | Simulated future action |
| `danger_center` | Would staying still be dangerous? | Simulated future action |
| `danger_right` | Would moving right be dangerous? | Simulated future action |

HC-2 link:

- Each frame becomes one input-record.
- The 10 features together are the kenmerkvector.
- Values are scaled because NN training works better with scaled inputs.

## 7. Player and Stone classes

### `Player`

The `Player` dataclass stores:

- `x`: horizontal position.
- `velocity`: current horizontal speed.

Important method:

```python
move(self, action, dt)
```

`action` is `-1`, `0` or `1`.
`dt` is delta time in seconds, so movement is frame-rate independent.

### `Stone`

The `Stone` dataclass stores:

- `x`: horizontal position.
- `y`: vertical position.
- `radius`: size.
- `speed`: falling speed.

Important method:

```python
update(self, dt)
```

This moves the stone down each frame.

## 8. Collision detection

Both player and stone have a `rect` property.

PyGame uses rectangles for simple collision detection:

```python
player.rect.colliderect(stone.rect)
```

This is an approximation because stones are drawn as circles but checked as
rectangles. It is simple and fast enough for the assignment.

## 9. TrainingLogger

`TrainingLogger` writes data to CSV.

Each row contains:

- timestamp
- current score
- all 10 features
- action taken by the human

This turns gameplay into supervised learning data:

```text
X = game-state features
y = human action
```

HC link:

- The dataset contains input-output examples.
- Training adjusts weights so the NN maps similar input-states to similar
  actions.

## 10. Feature engineering

The important function is:

```python
extract_features(player, stones)
```

It chooses the nearest dangerous stone and creates the 10-value input-vector.

### `nearest_dangerous_stone`

This function chooses the stone with the smallest time-to-reach the player.

Why:

- The AI should react to the most urgent threat.
- It keeps the input-vector small.

### `danger_for_action`

This function simulates the future position for one action:

- left
- stay
- right

It returns 1 if that action is dangerous, otherwise 0.

This gives the NN more useful information than raw coordinates alone.

## 11. Action sources

The game has three modes:

| Mode | Function | Meaning |
|---|---|---|
| `human` | `human_action()` | Keyboard controls, records data |
| `heuristic` | `heuristic_action()` | Rule-based demo, no NN |
| `ai` | `ai_action()` | Neural network predicts action |

### Human mode

You play the game. The CSV logs your decisions.

### Heuristic mode

This is a simple rule-based player.
It is useful as a comparison because it does not learn.

### AI mode

The trained model predicts:

```python
model.predict(...)
```

or, if possible:

```python
model.predict_proba(...)
```

The code reduces the probability of action `0` because gameplay data often has
many rows where the player is standing still. Without this correction, the AI
can become too passive.

## 12. Main game loop

`run_game(args)` contains the loop.

Every frame:

1. Calculate `dt`.
2. Process quit/restart events.
3. Extract features.
4. Decide action based on mode.
5. Move player.
6. Record row if in human mode.
7. Spawn stones.
8. Move stones.
9. Update score.
10. Check collisions.
11. Draw the screen.

This is the full data cycle:

```text
game state -> features -> action -> movement -> new game state
```

## 13. `train_model.py` purpose

`train_model.py` takes `data/training_data.csv` and trains a neural network.

The model is:

```python
StandardScaler() -> MLPClassifier()
```

### Why `StandardScaler`

It scales features to a comparable range.
This follows HC-2's point about scaling input data before giving it to a NN.

### Why `MLPClassifier`

The output is a class:

- left
- stay
- right

So a classifier is the correct model type.

## 14. Training data validation

`load_dataset()` checks:

- required columns exist;
- missing values are removed;
- `action` is integer;
- dataset has enough rows;
- dataset has at least two action classes.

Why:

- A NN cannot learn a movement policy from only one action.
- If every row says action `0`, the model learns to always stand still.

## 15. Class balancing

`balance_training_classes()` oversamples minority action classes.

Problem:

- In human gameplay, most frames may be action `0`.
- The model can get high accuracy by always predicting `0`.
- That is bad gameplay.

Solution:

- Duplicate rows from smaller classes until all classes have similar counts.

Effect:

- The model gets more training signal for left and right.
- Test accuracy may change, but F1-macro becomes more meaningful.

## 16. Hyperparameters in Practicum 4

### `hidden_layer_sizes`

Used in `MLPClassifier`.

Values:

```python
(8,)
(16,)
(32,)
(16, 8)
(32, 16)
(32, 16, 8)
```

Meaning:

- `(8,)` is 1 hidden layer with 8 nodes.
- `(16, 8)` is 2 hidden layers.
- `(32, 16, 8)` is 3 hidden layers.

Effect:

- More nodes/layers means more connecties and weights.
- More capacity can learn more complex movement patterns.
- More capacity needs more data and CPU time.
- Too much capacity can overfit.

HC-2 link: architecture varies by number of hidden layers and nodes per layer.

### `learning_rate_init`

Values:

```python
0.0005
0.001
0.01
```

Meaning:

- Controls the size of weight updates during training.

Effect:

- `0.0005`: stable but slower.
- `0.001`: balanced default.
- `0.01`: faster but may overshoot and produce unstable loss.

HC link: training uses error to adjust connectiegewichten.

### `max_iter`

Values:

```python
150
200
250
300
```

Meaning:

- Maximum number of training iterations/epochs.

Effect:

- Too low: underfitting.
- Too high: more time and more overfitting risk.
- `actual_iterations` in the log shows how many iterations were actually used.

HC-2 link: more training can lower error, but endless training can cause
overfitting.

### `alpha`

Value:

```python
0.0001
```

Meaning:

- L2 regularisation.
- Penalises very large weights.

Effect:

- Helps prevent overfitting.
- Higher alpha makes the model simpler.
- Lower alpha gives the model more freedom.

### `activation`

Value:

```python
activation="relu"
```

Meaning:

- ReLU is the activatiefunctie `h()`.

Effect:

- Adds non-linearity.
- Allows hidden layers to learn more than a linear relation.
- Cheap to compute.

HC-1 link: activation functions make the network non-linear.

### `solver`

Value:

```python
solver="adam"
```

Meaning:

- Adam is the algorithm that updates weights.

Effect:

- Usually works well as a default.
- Adapts update size per weight.

### `random_state`

Value:

```python
random_state=42
```

Effect:

- Makes sampling, splitting and training more reproducible.

### `DATASET_FRACTIONS`

Values:

```python
0.25
0.5
1.0
```

Meaning:

- Train experiments on 25 percent, 50 percent and 100 percent of the data.

Effect:

- Smaller data: faster, but less variation.
- More data: better generalisation, but slower training.
- Useful for showing how dataset size affects performance.

### `test_size`

Used inside:

```python
train_test_split(..., test_size=0.2)
```

Meaning:

- 20 percent of data is kept for testing.

Effect:

- Gives an unseen set to measure generalisation.
- If test data is too small, results are noisy.
- If test data is too large, less data remains for training.

## 17. Metrics in Practicum 4

The script logs:

| Metric | Meaning |
|---|---|
| `train_accuracy` | Accuracy on training data |
| `test_accuracy` | Accuracy on unseen test data |
| `train_f1_macro` | F1 averaged over classes on train |
| `test_f1_macro` | F1 averaged over classes on test |
| `final_loss` | Final training loss |
| `actual_iterations` | Actual number of training iterations |

Why F1-macro matters:

- It gives equal importance to left, stay and right.
- This helps when the dataset has many `stay` rows.

## 18. How to interpret results

Good model:

- high test F1-macro
- train and test scores are close
- confusion matrix shows all actions learned
- AI survives in the game and moves before danger is too close

Overfitting:

- train accuracy high
- test accuracy/F1 much lower
- AI behaves badly in new situations

Underfitting:

- train and test both low
- model is too small, data is poor or training too short

Dataset issue:

- AI freezes: too many action `0` rows.
- AI always moves one direction: data/action balance problem.
- AI reacts too late: features do not show danger early enough, or human data
  reacts too late.

## 19. Transparent limitations

This is not a perfect game AI.

Known simplifications:

- It only looks at one dangerous stone, not all stones.
- Collision is rectangle-based even though stones are circles.
- Human data may contain mistakes.
- The AI imitates your actions; it does not discover a better strategy by itself.
- The probability penalty for action `0` is a manual correction.
- It is supervised learning, not reinforcement learning.

These limitations are acceptable for the practicum because the focus is showing
how a neural network can replace a human player in a different context.

