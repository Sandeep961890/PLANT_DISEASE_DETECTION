import os
import argparse

from sklearn.model_selection import train_test_split

from preprocess import (
    load_dataset_paths,
    preprocess_image
)

from feature_extractor import (
    FeatureExtractor,
    get_device_info
)

from svm_classifier import (
    train_and_save_svm,
    evaluate_and_plot,
    predict_with_confidence
)


# =========================================================
# MAIN TRAINING FUNCTION
# =========================================================

def main(dataset_dir: str, out_dir: str):

    print("\n===================================")
    print(" CORN DISEASE TRAINING ")
    print("===================================\n")

    # =====================================================
    # DEVICE INFO
    # =====================================================

    print("Device Information:")
    print(get_device_info())

    # =====================================================
    # LOAD DATASET
    # =====================================================

    paths = []
    labels = []

    print("\nLoading dataset...\n")

    for img_path, label in load_dataset_paths(dataset_dir):

        paths.append(img_path)

        labels.append(label)

    print(f"\nTotal Images Found: {len(paths)}")

    # =====================================================
    # TRAIN / VALIDATION SPLIT
    # =====================================================

    train_p, val_p, train_y, val_y = train_test_split(
        paths,
        labels,
        test_size=0.2,
        stratify=labels,
        random_state=42
    )

    print(f"\nTraining Images   : {len(train_p)}")
    print(f"Validation Images : {len(val_p)}")

    # =====================================================
    # FEATURE EXTRACTION
    # =====================================================

    fe = FeatureExtractor(batch_size=32)

    # ---------------- TRAIN FEATURES ----------------

    print("\nExtracting Training Features...\n")

    X_train, train_y = fe.extract_from_paths(
        train_p,
        train_y,
        preprocess_image
    )

    print(f"\nTraining Feature Shape: {X_train.shape}")

    # ---------------- VALIDATION FEATURES ----------------

    print("\nExtracting Validation Features...\n")

    X_val, val_y = fe.extract_from_paths(
        val_p,
        val_y,
        preprocess_image
    )

    print(f"\nValidation Feature Shape: {X_val.shape}")

    # =====================================================
    # TRAIN SVM
    # =====================================================

    print("\nTraining SVM Classifier...\n")

    model, le = train_and_save_svm(
        X_train,
        train_y,
        out_dir,
        model_name='corn_svm_model'
    )

    # =====================================================
    # EVALUATE MODEL
    # =====================================================

    print("\nEvaluating Model...\n")

    metrics = evaluate_and_plot(
        model,
        le,
        X_val,
        val_y,
        out_dir,
        prefix='corn_'
    )

    # =====================================================
    # FINAL RESULTS
    # =====================================================

    print("\n===================================")
    print(" TRAINING COMPLETED ")
    print("===================================\n")

    print(
        f"Validation Accuracy: "
        f"{metrics['accuracy']:.4f}"
    )

    # =====================================================
    # SAMPLE PREDICTIONS
    # =====================================================

    print("\nRunning Sample Predictions...\n")

    sample_features = X_val[:5]

    pred_labels, confidences = predict_with_confidence(
        model,
        le,
        sample_features
    )

    for idx in range(len(pred_labels)):

        print(
            f"Prediction {idx+1}: "
            f"{pred_labels[idx]} "
            f"({confidences[idx]:.2f}%)"
        )

    # =====================================================
    # SAVED OUTPUTS
    # =====================================================

    print("\nSaved Outputs:")

    print(f"- Model Folder         → {out_dir}")
    print("- Confusion Matrix     → PNG")
    print("- Classification Report → TXT")
    print("- Accuracy Report      → TXT")

    print("\n===================================\n")


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--dataset',
        default='dataset/corn/data',
        help='Path to corn dataset folder'
    )

    parser.add_argument(
        '--out',
        default='outputs/corn',
        help='Output directory'
    )

    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    main(args.dataset, args.out)