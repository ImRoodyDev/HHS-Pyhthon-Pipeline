import argparse
from pathlib import Path

joblib = None
plt = None
pd = None
ConfusionMatrixDisplay = None
accuracy_score = None
classification_report = None
f1_score = None
train_test_split = None
MLPClassifier = None
Pipeline = None
StandardScaler = None


FEATURE_COLUMNS = [
    "player_x_norm",
    "player_velocity_norm",
    "stone_x_norm",
    "stone_y_norm",
    "stone_speed_norm",
    "dx_norm",
    "abs_dx_norm",
    "danger_left",
    "danger_center",
    "danger_right",
]


EXPERIMENTS = [
    {"hidden_layer_sizes": (8,), "learning_rate_init": 0.001, "max_iter": 150, "alpha": 0.0001},
    {"hidden_layer_sizes": (16,), "learning_rate_init": 0.001, "max_iter": 200, "alpha": 0.0001},
    {"hidden_layer_sizes": (32,), "learning_rate_init": 0.001, "max_iter": 250, "alpha": 0.0001},
    {"hidden_layer_sizes": (16, 8), "learning_rate_init": 0.001, "max_iter": 250, "alpha": 0.0001},
    {"hidden_layer_sizes": (32, 16), "learning_rate_init": 0.001, "max_iter": 300, "alpha": 0.0001},
    {"hidden_layer_sizes": (32, 16, 8), "learning_rate_init": 0.001, "max_iter": 300, "alpha": 0.0001},
    {"hidden_layer_sizes": (16, 8), "learning_rate_init": 0.0005, "max_iter": 300, "alpha": 0.0001},
    {"hidden_layer_sizes": (16, 8), "learning_rate_init": 0.01, "max_iter": 200, "alpha": 0.0001},
]

DATASET_FRACTIONS = [0.25, 0.5, 1.0]


def load_dependencies():
    global joblib
    global plt
    global pd
    global ConfusionMatrixDisplay
    global accuracy_score
    global classification_report
    global f1_score
    global train_test_split
    global MLPClassifier
    global Pipeline
    global StandardScaler

    import joblib as joblib_module
    import matplotlib.pyplot as plt_module
    import pandas as pd_module
    from sklearn.metrics import (
        ConfusionMatrixDisplay as ConfusionMatrixDisplay_class,
        accuracy_score as accuracy_score_function,
        classification_report as classification_report_function,
        f1_score as f1_score_function,
    )
    from sklearn.model_selection import train_test_split as train_test_split_function
    from sklearn.neural_network import MLPClassifier as MLPClassifier_class
    from sklearn.pipeline import Pipeline as Pipeline_class
    from sklearn.preprocessing import StandardScaler as StandardScaler_class

    joblib = joblib_module
    plt = plt_module
    pd = pd_module
    ConfusionMatrixDisplay = ConfusionMatrixDisplay_class
    accuracy_score = accuracy_score_function
    classification_report = classification_report_function
    f1_score = f1_score_function
    train_test_split = train_test_split_function
    MLPClassifier = MLPClassifier_class
    Pipeline = Pipeline_class
    StandardScaler = StandardScaler_class


def load_dataset(path):
    df = pd.read_csv(path)
    missing = [column for column in FEATURE_COLUMNS + ["action"] if column not in df.columns]
    if missing:
        raise ValueError(f"Dataset mist kolommen: {missing}")

    df = df.dropna(subset=FEATURE_COLUMNS + ["action"]).copy()
    df["action"] = df["action"].astype(int)

    if len(df) < 30:
        raise ValueError("Verzamel eerst meer data. Richtlijn: minimaal een paar honderd rijen.")

    class_counts = df["action"].value_counts()
    if len(class_counts) < 2:
        raise ValueError("De dataset bevat maar een actieklasse. Speel meer gevarieerd: links, rechts en soms blijven staan.")

    return df


def balance_training_classes(X_train, y_train):
    """Oversample minority action classes so every class has the same count as the majority.
    This prevents the model from learning to always predict 'stay still' (action=0)."""
    from sklearn.utils import resample
    combined = X_train.copy()
    combined["__label__"] = y_train.values
    max_count = combined["__label__"].value_counts().max()
    parts = []
    for _, group in combined.groupby("__label__"):
        if len(group) < max_count:
            group = resample(group, replace=True, n_samples=max_count, random_state=42)
        parts.append(group)
    balanced = pd.concat(parts).sample(frac=1, random_state=42).reset_index(drop=True)
    return balanced.drop("__label__", axis=1), balanced["__label__"]


def build_model(config):
    return Pipeline(
        steps=[
            ("scale", StandardScaler()),
            (
                "nn",
                MLPClassifier(
                    hidden_layer_sizes=config["hidden_layer_sizes"],
                    learning_rate_init=config["learning_rate_init"],
                    max_iter=config["max_iter"],
                    alpha=config["alpha"],
                    activation="relu",
                    solver="adam",
                    random_state=42,
                ),
            ),
        ]
    )


def train_experiments(df):
    results = []
    trained = []

    experiment_id = 0
    for fraction in DATASET_FRACTIONS:
        if fraction < 1.0:
            sample_df = df.sample(frac=fraction, random_state=42).copy()
        else:
            sample_df = df.copy()

        X = sample_df[FEATURE_COLUMNS]
        y = sample_df["action"]
        stratify = y if y.value_counts().min() >= 2 else None

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=stratify,
        )

        # Balance classes so "stay still" doesn't dominate the training signal
        X_train, y_train = balance_training_classes(X_train, y_train)

        for config in EXPERIMENTS:
            experiment_id += 1
            print(f"Experiment {experiment_id}: fraction={fraction}, config={config}")

            model = build_model(config)
            model.fit(X_train, y_train)

            train_pred = model.predict(X_train)
            test_pred = model.predict(X_test)
            nn = model.named_steps["nn"]

            row = {
                "experiment_id": experiment_id,
                "dataset_fraction": fraction,
                "dataset_rows": len(sample_df),
                "train_rows": len(X_train),
                "test_rows": len(X_test),
                "hidden_layer_sizes": str(config["hidden_layer_sizes"]),
                "hidden_layer_count": len(config["hidden_layer_sizes"]),
                "hidden_nodes_total": sum(config["hidden_layer_sizes"]),
                "learning_rate": config["learning_rate_init"],
                "epochs": config["max_iter"],
                "alpha": config["alpha"],
                "train_accuracy": accuracy_score(y_train, train_pred),
                "test_accuracy": accuracy_score(y_test, test_pred),
                "train_f1_macro": f1_score(y_train, train_pred, average="macro"),
                "test_f1_macro": f1_score(y_test, test_pred, average="macro"),
                "actual_iterations": nn.n_iter_,
                "final_loss": nn.loss_,
            }
            results.append(row)
            trained.append(
                {
                    "row": row,
                    "model": model,
                    "X_test": X_test,
                    "y_test": y_test,
                    "test_pred": test_pred,
                }
            )

    results_df = pd.DataFrame(results).sort_values("test_f1_macro", ascending=False).reset_index(drop=True)
    best_id = int(results_df.iloc[0]["experiment_id"])
    best_run = next(item for item in trained if item["row"]["experiment_id"] == best_id)
    return results_df, best_run


def save_outputs(results_df, best_run, output_dir, model_path):
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path.parent.mkdir(parents=True, exist_ok=True)

    results_csv = output_dir / "experiment_results.csv"
    results_xlsx = output_dir / "experiment_results.xlsx"
    report_txt = output_dir / "best_classification_report.txt"
    accuracy_plot = output_dir / "experiment_accuracy.png"
    confusion_plot = output_dir / "best_confusion_matrix.png"

    results_df.to_csv(results_csv, index=False)
    with pd.ExcelWriter(results_xlsx, engine="openpyxl") as writer:
        results_df.to_excel(writer, sheet_name="Experiments", index=False)
        results_df.head(5).to_excel(writer, sheet_name="Top 5", index=False)

    report = classification_report(best_run["y_test"], best_run["test_pred"])
    report_txt.write_text(report, encoding="utf-8")

    plot_df = results_df.sort_values("experiment_id")
    plt.figure(figsize=(11, 5))
    plt.plot(plot_df["experiment_id"], plot_df["train_accuracy"], marker="o", label="Train accuracy")
    plt.plot(plot_df["experiment_id"], plot_df["test_accuracy"], marker="o", label="Test accuracy")
    plt.xlabel("Experiment")
    plt.ylabel("Accuracy")
    plt.title("Train/test accuracy per experiment")
    plt.legend()
    plt.tight_layout()
    plt.savefig(accuracy_plot, dpi=140)
    plt.close()

    ConfusionMatrixDisplay.from_predictions(best_run["y_test"], best_run["test_pred"])
    plt.title("Best model confusion matrix")
    plt.tight_layout()
    plt.savefig(confusion_plot, dpi=140)
    plt.close()

    joblib.dump(
        {
            "model": best_run["model"],
            "feature_columns": FEATURE_COLUMNS,
            "best_experiment": best_run["row"],
        },
        model_path,
    )

    return {
        "results_csv": results_csv,
        "results_xlsx": results_xlsx,
        "report_txt": report_txt,
        "accuracy_plot": accuracy_plot,
        "confusion_plot": confusion_plot,
        "model_path": model_path,
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Train neural-network player for Practicum 4")
    parser.add_argument("--data", default="data/training_data.csv", help="CSV with collected human gameplay data")
    parser.add_argument("--logs", default="logs", help="Output folder for experiment logs")
    parser.add_argument("--model", default="models/best_model.joblib", help="Output model path")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    load_dependencies()
    df = load_dataset(args.data)
    print("Dataset rows:", len(df))
    print("Action counts:")
    print(df["action"].value_counts().sort_index())

    results_df, best_run = train_experiments(df)
    outputs = save_outputs(results_df, best_run, Path(args.logs), Path(args.model))

    print("\nBeste experiment:")
    print(pd.Series(best_run["row"]))
    print("\nOutputs:")
    for name, path in outputs.items():
        print(f"{name}: {path}")
