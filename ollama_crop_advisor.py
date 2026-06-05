import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import argparse
import json
import subprocess
import re

from config import Config
from predict_disease import (
    load_model,
    predict_disease,
    MODEL_CONFIG
)

from preprocess import preprocess_image
from feature_extractor import FeatureExtractor

import numpy as np


# =========================================================
# GET DISEASE FROM MODEL
# =========================================================

def get_disease_prediction(
    crop_name,
    image_path,
    model,
    label_encoder,
    feature_extractor
):

    # -----------------------------------------
    # PREPROCESS IMAGE
    # -----------------------------------------

    img = preprocess_image(image_path)

    if img is None:

        print("[ERROR] Failed to preprocess image")

        return None, None

    # -----------------------------------------
    # CONVERT TO BATCH
    # -----------------------------------------

    img_batch = np.expand_dims(img, axis=0)

    # -----------------------------------------
    # EXTRACT FEATURES
    # -----------------------------------------

    features = feature_extractor.extract_from_array(
        img_batch
    )

    # -----------------------------------------
    # PREDICT
    # -----------------------------------------

    probabilities = model.predict_proba(features)[0]

    pred_idx = np.argmax(probabilities)

    confidence = probabilities[pred_idx]

    disease_name = label_encoder.inverse_transform(
        [pred_idx]
    )[0]

    return disease_name, confidence


# =========================================================
# RECOMMENDATION HELPERS
# =========================================================

def _normalize_text(value):
    if value is None:
        return ""
    return str(value).strip()


def _severity_from_confidence(confidence):
    if confidence >= 0.85:
        return "High"
    if confidence >= 0.6:
        return "Moderate"
    return "Low"


def _parse_json_response(response_text):
    if not response_text:
        return None

    text = response_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except Exception:
        return None


def _parse_section_response(response_text):
    sections = {
        "disease_summary": "",
        "causes": "",
        "treatment": "",
        "fertilizer_name": "",
        "npk_values": "",
        "fertilizer_recommendation": "",
        "dosage": "",
        "application_timing": "",
        "spraying_interval": "",
        "organic_alternative": "",
        "prevention_tips": "",
        "recovery_plan": "",
        "severity": ""
    }

    if not response_text:
        return sections

    current_key = None
    header_map = {
        "disease summary": "disease_summary",
        "causes": "causes",
        "causes of disease": "causes",
        "treatment": "treatment",
        "treatment recommendations": "treatment",
        "fertilizer name": "fertilizer_name",
        "fertilizer formula": "npk_values",
        "npk values": "npk_values",
        "npk": "npk_values",
        "fertilizer recommendation": "fertilizer_recommendation",
        "fertilizer suggestions": "fertilizer_recommendation",
        "dosage": "dosage",
        "application timing": "application_timing",
        "spraying interval": "spraying_interval",
        "timing": "application_timing",
        "organic alternatives": "organic_alternative",
        "organic alternative": "organic_alternative",
        "prevention tips": "prevention_tips",
        "prevention": "prevention_tips",
        "7-day recovery plan": "recovery_plan",
        "recovery plan": "recovery_plan",
        "severity": "severity"
    }

    for raw_line in response_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        match = re.match(r"^(\d+)\.\s*(.+)$", line)
        if match:
            header = match.group(2).strip().lower().rstrip(":")
            current_key = header_map.get(header)
            if current_key and sections[current_key]:
                continue
            if current_key:
                sections[current_key] = ""
            continue

        if current_key:
            sections[current_key] = f"{sections[current_key]}\n{line}".strip()

    return sections


def _compose_full_text(data):
    parts = [
        ("Disease Summary", data.get("disease_summary")),
        ("Causes", data.get("causes")),
        ("Treatment", data.get("treatment")),
        ("Fertilizer Name", data.get("fertilizer_name")),
        ("NPK Values", data.get("npk_values")),
        ("Fertilizer Recommendation", data.get("fertilizer_recommendation")),
        ("Dosage", data.get("dosage")),
        ("Application Timing", data.get("application_timing")),
        ("Spraying Interval", data.get("spraying_interval")),
        ("Organic Alternatives", data.get("organic_alternative")),
        ("Prevention Tips", data.get("prevention_tips")),
        ("7-Day Recovery Plan", data.get("recovery_plan")),
    ]

    formatted = []
    for title, body in parts:
        clean_body = _normalize_text(body)
        if clean_body:
            formatted.append(f"{title}\n{clean_body}")

    if not formatted:
        return ""

    return "\n\n".join(formatted)


def _fallback_recommendation(crop_name, disease_name, confidence):
    severity = _severity_from_confidence(confidence)
    crop_label = crop_name.capitalize()

    data = {
        "severity": severity,
        "disease_summary": (
            f"{disease_name} has been detected on {crop_label} with {confidence * 100:.2f}% confidence. "
            f"This recommendation is designed to help slow spread, support recovery, and protect nearby plants."
        ),
        "causes": (
            "Likely contributors include excess humidity, leaf wetness, poor airflow, infected planting material, "
            "or delayed field sanitation."
        ),
        "treatment": (
            "Remove severely affected leaves, improve canopy airflow, and follow approved crop-protection practices "
            "recommended by local agricultural officers."
        ),
        "fertilizer_name": f"Balanced NPK 10-10-10 fertilizer for {crop_label}",
        "npk_values": "10-10-10",
        "fertilizer_recommendation": (
            f"Use a balanced fertilizer for {crop_label.lower()} with moderate nitrogen and adequate potassium to "
            "support recovery without forcing weak new growth."
        ),
        "dosage": "Apply a light corrective dose according to soil test results or label guidance. Avoid over-fertilizing stressed plants.",
        "application_timing": "Apply after removing infected tissue and when foliage is dry, preferably early morning or late afternoon.",
        "application_schedule": "Apply after removing infected tissue and when foliage is dry, preferably early morning or late afternoon.",
        "spraying_interval": "Repeat application every 7-10 days during recovery, or as directed by product label.",
        "fertilizer_notes": "Follow product label instructions, check local extension guidance, and avoid excess nitrogen on weakened plants.",
        "organic_alternative": (
            "Use well-decomposed compost, vermicompost, seaweed extract, or fermented plant-based bio-stimulants as safer support options."
        ),
        "prevention_tips": (
            "Maintain spacing, rotate crops, remove debris, keep tools clean, and monitor new symptoms closely for 7 days."
        ),
        "recovery_plan": (
            "Day 1-2: remove infected tissue and sanitize tools. Day 3-4: apply the first support treatment. "
            "Day 5-7: monitor new growth and repeat only if symptoms continue to spread."
        ),
    }
    data["application_schedule"] = data["application_timing"]
    data["full_text"] = _compose_full_text(data)
    data["raw_response"] = data["full_text"]
    return data


def _normalize_recommendation_payload(crop_name, disease_name, confidence, response_text):
    parsed = _parse_json_response(response_text)

    if parsed is None:
        parsed = _parse_section_response(response_text)

    normalized = {
        "severity": _normalize_text(parsed.get("severity")) or _severity_from_confidence(confidence),
        "disease_summary": _normalize_text(parsed.get("disease_summary")),
        "causes": _normalize_text(parsed.get("causes")),
        "treatment": _normalize_text(parsed.get("treatment")),
        "fertilizer_name": _normalize_text(parsed.get("fertilizer_name")),
        "npk_values": _normalize_text(parsed.get("npk_values")),
        "fertilizer_recommendation": _normalize_text(parsed.get("fertilizer_recommendation") or parsed.get("fertilizer")),
        "dosage": _normalize_text(parsed.get("dosage")),
        "application_timing": _normalize_text(parsed.get("application_timing") or parsed.get("application_schedule")),
        "application_schedule": _normalize_text(parsed.get("application_schedule") or parsed.get("application_timing")),
        "spraying_interval": _normalize_text(parsed.get("spraying_interval")),
        "fertilizer_notes": _normalize_text(parsed.get("fertilizer_notes")),
        "organic_alternative": _normalize_text(parsed.get("organic_alternative")),
        "prevention_tips": _normalize_text(parsed.get("prevention_tips") or parsed.get("prevention")),
        "recovery_plan": _normalize_text(parsed.get("recovery_plan") or parsed.get("seven_day_recovery_plan")),
    }

    if not any(normalized.values()):
        return _fallback_recommendation(crop_name, disease_name, confidence)

    normalized["application_schedule"] = normalized["application_timing"]
    normalized["full_text"] = _compose_full_text(normalized)
    normalized["raw_response"] = response_text.strip() if response_text else ""

    if not normalized["full_text"]:
        normalized = _fallback_recommendation(crop_name, disease_name, confidence)

    return normalized


# =========================================================
# OLLAMA RESPONSE
# =========================================================

def generate_ai_advice(
    crop_name,
    disease_name,
    confidence
):
    """
    Generate AI advice using Ollama.
    
    Args:
        crop_name: Name of crop (banana/corn/sugarcane)
        disease_name: Detected disease name
        confidence: Confidence score (0-1)
    
    Returns:
        dict: Structured AI recommendation data
    """

    prompt = f"""
You are an advanced Agricultural AI Advisor for farmers.

Crop Name: {crop_name}
Detected Disease: {disease_name}
Confidence Score: {confidence * 100:.2f}%

Return ONLY valid JSON with these exact keys:
{{
    "severity": "Low|Moderate|High",
    "disease_summary": "Short farmer-friendly summary",
    "causes": "Likely causes and conditions",
    "treatment": "Immediate treatment steps",
    "fertilizer_name": "Recommended fertilizer or blend name",
    "npk_values": "N-P-K formulation values",
    "fertilizer_recommendation": "Specific fertilizer recommendation",
    "dosage": "Practical dosage guidance",
    "application_timing": "When and how often to apply",
    "spraying_interval": "Recommended spraying interval",
    "organic_alternative": "Organic or low-input alternative",
    "prevention_tips": "Prevention guidance",
    "recovery_plan": "7-day recovery plan"
}}

Rules:
- Keep advice practical, safe, and crop-specific.
- Do not include markdown fences or extra commentary.
- Use simple language that a farmer can act on immediately.
- If you are uncertain, provide conservative guidance rather than risky advice.
"""

    print("\n===================================")
    print(" GENERATING AI ADVICE ")
    print("===================================\n")

    try:

        result = subprocess.run(
            [
                "ollama",
                "run",
                Config.OLLAMA_MODEL
            ],
            input=prompt,
            text=True,
            capture_output=True,
            encoding="utf-8",
            timeout=Config.OLLAMA_TIMEOUT
        )

        # Print to terminal for debugging
        print(result.stdout)
        advice_text = result.stdout.strip()

        if advice_text:
            print("\n[SUCCESS] AI Advice generated successfully")
            print("===================================\n")
            return _normalize_recommendation_payload(
                crop_name,
                disease_name,
                confidence,
                advice_text
            )

        print("[WARNING] Ollama returned empty response")
        return _fallback_recommendation(crop_name, disease_name, confidence)

    except subprocess.TimeoutExpired:
        print("[ERROR] Ollama request timed out (60 seconds)")
        return _fallback_recommendation(crop_name, disease_name, confidence)
    
    except Exception as e:
        print("[ERROR] Failed to generate Ollama response")
        print(f"Exception: {e}")
        return _fallback_recommendation(crop_name, disease_name, confidence)


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

    # -----------------------------------------
    # CHECK SUPPORTED CROPS
    # -----------------------------------------

    if crop_name not in MODEL_CONFIG:

        print("\n===================================")
        print(" ERROR ")
        print("===================================\n")

        print(f"Plant model not found for: {crop_name}")

        print("\nSupported Crops:")

        for crop in MODEL_CONFIG.keys():

            print(f"- {crop}")

        print("\n===================================\n")

        return

    # -----------------------------------------
    # LOAD FEATURE EXTRACTOR
    # -----------------------------------------

    print("\nLoading Feature Extractor...\n")

    fe = FeatureExtractor(batch_size=1)

    # -----------------------------------------
    # LOAD MODEL
    # -----------------------------------------

    model, label_encoder = load_model(crop_name)

    if model is None:

        return

    # -----------------------------------------
    # GET PREDICTION
    # -----------------------------------------

    disease_name, confidence = get_disease_prediction(
        crop_name,
        image_path,
        model,
        label_encoder,
        fe
    )

    if disease_name is None:

        return

    # -----------------------------------------
    # SHOW PREDICTION
    # -----------------------------------------

    print("\n===================================")
    print(" DISEASE DETECTION RESULT ")
    print("===================================\n")

    print(f"Crop Name         : {crop_name}")

    print(f"Predicted Disease : {disease_name}")

    print(
        f"Confidence Score  : "
        f"{confidence * 100:.2f}%"
    )

    print("\n===================================\n")

    # -----------------------------------------
    # GENERATE OLLAMA AI RESPONSE
    # -----------------------------------------

    generate_ai_advice(
        crop_name,
        disease_name,
        confidence
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == '__main__':

    main()