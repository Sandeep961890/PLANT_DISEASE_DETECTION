import os
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def train_and_save_svm(features: np.ndarray, labels: list, out_dir: str, model_name: str = 'svm_model'):
    os.makedirs(out_dir, exist_ok=True)
    le = LabelEncoder()
    y = le.fit_transform(labels)

    scaler = StandardScaler()
    clf = SVC(kernel='rbf', probability=True)
    pipeline = Pipeline([('scaler', scaler), ('svc', clf)])
    pipeline.fit(features, y)

    joblib.dump(pipeline, os.path.join(out_dir, f'{model_name}.pkl'))
    joblib.dump(le, os.path.join(out_dir, 'label_encoder.pkl'))
    return pipeline, le


def evaluate_and_plot(pipeline, le, X_val, y_val, out_dir: str, prefix: str = ''):
    os.makedirs(out_dir, exist_ok=True)
    y_true = le.transform(y_val)
    y_pred = pipeline.predict(X_val)
    acc = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred, target_names=le.classes_)
    cm = confusion_matrix(y_true, y_pred)

    with open(os.path.join(out_dir, f'{prefix}classification_report.txt'), 'w') as f:
        f.write(report)

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=le.classes_, yticklabels=le.classes_)
    plt.ylabel('True')
    plt.xlabel('Predicted')
    plt.title('Confusion Matrix')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f'{prefix}confusion_matrix.png'))
    plt.close()

    return {'accuracy': acc, 'report': report, 'confusion_matrix': cm}


def predict_with_confidence(pipeline, le, features: np.ndarray):
    probs = pipeline.predict_proba(features)
    idx = probs.argmax(axis=1)
    labels = le.inverse_transform(idx)
    confs = probs.max(axis=1)
    return labels, confs
