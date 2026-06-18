import os
import joblib
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# =========================================================
# TRAIN AND SAVE SVM
# =========================================================

def train_and_save_svm(
    features: np.ndarray,
    labels: list,
    out_dir: str,
    model_name: str = "svm_model"
):

    os.makedirs(out_dir, exist_ok=True)

    if len(features) == 0:
        raise ValueError(
            "Feature array is empty."
        )

    if len(labels) == 0:
        raise ValueError(
            "Label list is empty."
        )

    # Encode labels
    le = LabelEncoder()

    y = le.fit_transform(labels)

    print("\n===================================")
    print(" SVM TRAINING ")
    print("===================================\n")

    print(f"Number of Samples : {len(y)}")
    print(f"Number of Classes : {len(le.classes_)}")
    print(f"Classes           : {list(le.classes_)}")

    # Must have at least 2 classes
    if len(le.classes_) < 2:

        raise ValueError(
            f"SVM requires at least 2 classes. "
            f"Found only: {list(le.classes_)}"
        )

    pipeline = Pipeline([
        (
            "scaler",
            StandardScaler()
        ),
        (
            "svc",
            SVC(
                kernel="rbf",
                probability=True,
                random_state=42
            )
        )
    ])

    pipeline.fit(features, y)

    model_path = os.path.join(
        out_dir,
        f"{model_name}.pkl"
    )

    encoder_path = os.path.join(
        out_dir,
        "label_encoder.pkl"
    )

    joblib.dump(
        pipeline,
        model_path
    )

    joblib.dump(
        le,
        encoder_path
    )

    print("\nModel Saved:")
    print(model_path)

    print("\nLabel Encoder Saved:")
    print(encoder_path)

    return pipeline, le


# =========================================================
# EVALUATE MODEL
# =========================================================

def evaluate_and_plot(
    pipeline,
    le,
    X_val,
    y_val,
    out_dir: str,
    prefix: str = ""
):

    os.makedirs(
        out_dir,
        exist_ok=True
    )

    y_true = le.transform(y_val)

    y_pred = pipeline.predict(X_val)

    acc = accuracy_score(
        y_true,
        y_pred
    )

    report = classification_report(
        y_true,
        y_pred,
        target_names=le.classes_
    )

    cm = confusion_matrix(
        y_true,
        y_pred
    )

    report_path = os.path.join(
        out_dir,
        f"{prefix}classification_report.txt"
    )

    with open(
        report_path,
        "w"
    ) as f:

        f.write(report)

    plt.figure(
        figsize=(8, 6)
    )

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=le.classes_,
        yticklabels=le.classes_
    )

    plt.ylabel("True")

    plt.xlabel("Predicted")

    plt.title(
        "Confusion Matrix"
    )

    plt.tight_layout()

    cm_path = os.path.join(
        out_dir,
        f"{prefix}confusion_matrix.png"
    )

    plt.savefig(
        cm_path,
        dpi=300
    )

    plt.close()

    print("\nValidation Accuracy:")
    print(f"{acc:.4f}")

    return {
        "accuracy": acc,
        "report": report,
        "confusion_matrix": cm
    }


# =========================================================
# PREDICTION
# =========================================================

def predict_with_confidence(
    pipeline,
    le,
    features: np.ndarray
):

    probs = pipeline.predict_proba(
        features
    )

    idx = probs.argmax(
        axis=1
    )

    labels = le.inverse_transform(
        idx
    )

    confidences = probs.max(
        axis=1
    )

    return labels, confidences


# =========================================================
# TEST MODULE
# =========================================================

if __name__ == "__main__":

    print("\n===================================")
    print(" SVM CLASSIFIER MODULE ")
    print("===================================\n")

    print(
        "Module loaded successfully."
    )