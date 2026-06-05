import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import argparse
import joblib
import numpy as np

from preprocess import preprocess_image
from feature_extractor import FeatureExtractor


# =========================================================
# MODEL CONFIGURATION
# =========================================================

MODEL_CONFIG = {

    "banana": {
        "model": "outputs/banana/banana_svm_model.pkl",
        "encoder": "outputs/banana/label_encoder.pkl"
    },

    "corn": {
        "model": "outputs/corn/corn_svm_model.pkl",
        "encoder": "outputs/corn/label_encoder.pkl"
    },

    "sugarcane": {
        "model": "outputs/sugarcane/sugarcane_svm_model.pkl",
        "encoder": "outputs/sugarcane/label_encoder.pkl"
    }
}


# =========================================================
# LOAD MODEL
# =========================================================

def load_model(crop_name):

    crop_name = crop_name.lower()

    # -----------------------------------------------------
    # CHECK SUPPORTED CROPS
    # -----------------------------------------------------

    if crop_name not in MODEL_CONFIG:

        print("\n===================================")
        print(" ERROR ")
        print("===================================\n")

        print(f"Plant model not found for: {crop_name}")

        print("\nSupported Crops:")

        for crop in MODEL_CONFIG.keys():

            print(f"- {crop}")

        print("\n===================================\n")

        return None, None

    # -----------------------------------------------------
    # GET MODEL PATHS
    # -----------------------------------------------------

    model_path = MODEL_CONFIG[crop_name]["model"]

    encoder_path = MODEL_CONFIG[crop_name]["encoder"]

    # -----------------------------------------------------
    # CHECK MODEL FILES
    # -----------------------------------------------------

    if not os.path.exists(model_path):

        print("\n===================================")
        print(" ERROR ")
        print("===================================\n")

        print(f"Model file not found:\n{model_path}")

        print("\n===================================\n")

        return None, None

    if not os.path.exists(encoder_path):

        print("\n===================================")
        print(" ERROR ")
        print("===================================\n")

        print(f"Label encoder not found:\n{encoder_path}")

        print("\n===================================\n")

        return None, None

    # -----------------------------------------------------
    # LOAD MODEL
    # -----------------------------------------------------

    print("\nLoading Model...\n")

    model = joblib.load(model_path)

    print("Loading Label Encoder...\n")

    label_encoder = joblib.load(encoder_path)

    return model, label_encoder


# =========================================================
# PREDICT DISEASE
# =========================================================

def predict_disease(
    crop_name,
    image_path,
    model,
    label_encoder,
    feature_extractor
):

    # -----------------------------------------------------
    # CHECK IMAGE
    # -----------------------------------------------------

    if not os.path.exists(image_path):

        print("\n===================================")
        print(" ERROR ")
        print("===================================\n")

        print(f"Image not found:\n{image_path}")

        print("\n===================================\n")

        return

    # -----------------------------------------------------
    # PREPROCESS IMAGE
    # -----------------------------------------------------

    print("\nPreprocessing Image...\n")

    img = preprocess_image(image_path)

    if img is None:

        print("\n===================================")
        print(" ERROR ")
        print("===================================\n")

        print("Failed to preprocess image")

        print("\n===================================\n")

        return

    # -----------------------------------------------------
    # CONVERT TO BATCH
    # -----------------------------------------------------

    img_batch = np.expand_dims(img, axis=0)

    # -----------------------------------------------------
    # FEATURE EXTRACTION
    # -----------------------------------------------------

    print("Extracting Features...\n")

    features = feature_extractor.extract_from_array(
        img_batch
    )

    # -----------------------------------------------------
    # PREDICTION
    # -----------------------------------------------------

    print("Predicting Disease...\n")

    probabilities = model.predict_proba(features)[0]

    pred_idx = np.argmax(probabilities)

    confidence = probabilities[pred_idx]

    disease_name = label_encoder.inverse_transform(
        [pred_idx]
    )[0]

    # -----------------------------------------------------
    # RESULTS
    # -----------------------------------------------------

    print("\n===================================")
    print(" DISEASE PREDICTION RESULT ")
    print("===================================\n")

    print(f"Crop Name         : {crop_name}")

    print(f"Image Path        : {image_path}")

    print(f"\nPredicted Disease : {disease_name}")

    print(
        f"Confidence Score  : "
        f"{confidence * 100:.2f}%"
    )

    # -----------------------------------------------------
    # ALL CLASS PROBABILITIES
    # -----------------------------------------------------

    print("\nClass Probabilities:\n")

    for idx, cls in enumerate(label_encoder.classes_):

        prob = probabilities[idx] * 100

        print(f"{cls:<20} : {prob:.2f}%")

    print("\n===================================\n")


# =========================================================
# MAIN
# =========================================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--crop',
        required=True,
        help='Crop name: banana / corn / sugarcane'
    )

    parser.add_argument(
        '--image',
        required=True,
        help='Path to test image'
    )

    args = parser.parse_args()

    crop_name = args.crop.lower()

    image_path = args.image

    # -----------------------------------------------------
    # LOAD FEATURE EXTRACTOR
    # -----------------------------------------------------

    print("\nLoading Feature Extractor...\n")

    fe = FeatureExtractor(batch_size=1)

    # -----------------------------------------------------
    # LOAD MODEL
    # -----------------------------------------------------

    model, label_encoder = load_model(crop_name)

    # -----------------------------------------------------
    # STOP IF MODEL NOT FOUND
    # -----------------------------------------------------

    if model is None or label_encoder is None:

        return

    # -----------------------------------------------------
    # PREDICT DISEASE
    # -----------------------------------------------------

    predict_disease(
        crop_name,
        image_path,
        model,
        label_encoder,
        fe
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == '__main__':

    main()