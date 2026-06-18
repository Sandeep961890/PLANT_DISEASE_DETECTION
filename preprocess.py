import os
import cv2
import numpy as np

from typing import (
    Tuple,
    Optional,
    Generator
)


# =========================================================
# SAFE IMAGE READER
# =========================================================

def read_image_safe(
    path: str
) -> Optional[np.ndarray]:

    """
    Safely read image from disk.
    Supports unicode paths and
    corrupted image handling.
    """

    try:

        img = cv2.imdecode(
            np.fromfile(
                path,
                dtype=np.uint8
            ),
            cv2.IMREAD_COLOR
        )

        if img is None:

            print(
                f"[WARNING] Unable to read image:\n{path}"
            )

            return None

        return img

    except Exception as e:

        print(
            f"[ERROR] Failed reading image:\n{path}"
        )

        print(e)

        return None


# =========================================================
# CLAHE ENHANCEMENT
# =========================================================

def clahe_enhance(
    img: np.ndarray
) -> np.ndarray:

    """
    Apply CLAHE enhancement
    to improve disease visibility.
    """

    lab = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2LAB
    )

    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=3.0,
        tileGridSize=(8, 8)
    )

    l_clahe = clahe.apply(l)

    merged = cv2.merge(
        (l_clahe, a, b)
    )

    enhanced = cv2.cvtColor(
        merged,
        cv2.COLOR_LAB2BGR
    )

    return enhanced


# =========================================================
# IMAGE PREPROCESSING
# =========================================================

def preprocess_image(
    path: str,
    size: Tuple[int, int] = (224, 224)
) -> Optional[np.ndarray]:

    """
    Complete preprocessing pipeline.
    """

    img = read_image_safe(path)

    if img is None:
        return None

    try:

        # Noise reduction
        img = cv2.GaussianBlur(
            img,
            (3, 3),
            0
        )

        # CLAHE enhancement
        img = clahe_enhance(img)

        # BGR -> RGB
        img = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2RGB
        )

        # Resize
        img = cv2.resize(
            img,
            size,
            interpolation=cv2.INTER_AREA
        )

        # Normalize
        img = img.astype(
            np.float32
        ) / 255.0

        return img

    except Exception as e:

        print(
            f"[ERROR] Failed preprocessing:\n{path}"
        )

        print(e)

        return None


# =========================================================
# DATASET LOADER
# =========================================================

def load_dataset_paths(
    root_dir: str
) -> Generator[Tuple[str, str], None, None]:

    """
    Universal Dataset Loader

    Supports structures like:

    dataset/banana/
        BananaLSD/
            AugmentedSet/
                healthy/
                cordana/
                pestalotiopsis/
                sigatoka/

    dataset/corn/
        data/
            Healthy/
            Blight/
            Common_Rust/
            Gray_Leaf_Spot/

    dataset/sugarcane/
        BacterialBlights/
        healthy/
        Mosaic/
        red_rot/
        rust/
        Yellow/

    Returns:
        image_path, class_label
    """

    if not os.path.exists(root_dir):

        raise FileNotFoundError(
            f"Dataset not found: {root_dir}"
        )

    valid_extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".tif",
        ".tiff",
        ".webp"
    )

    class_counts = {}

    total_images = 0

    # ============================================
    # Walk entire dataset tree
    # ============================================

    for current_root, dirs, files in os.walk(root_dir):

        image_files = [
            f for f in files
            if f.lower().endswith(valid_extensions)
        ]

        # Skip folders without images
        if len(image_files) == 0:
            continue

        # Use current folder name as label
        class_name = os.path.basename(
            current_root
        ).lower()

        image_count = 0

        for fname in image_files:

            image_path = os.path.join(
                current_root,
                fname
            )

            image_count += 1
            total_images += 1

            yield image_path, class_name

        class_counts[class_name] = (
            class_counts.get(
                class_name,
                0
            )
            + image_count
        )

    # ============================================
    # Dataset Summary
    # ============================================

    print("\n===================================")
    print(" DATASET SUMMARY ")
    print("===================================\n")

    print(
        f"Classes Found: "
        f"{sorted(class_counts.keys())}\n"
    )

    for cls in sorted(
        class_counts.keys()
    ):

        print(
            f"[INFO] Loaded "
            f"{class_counts[cls]} "
            f"images from class: {cls}"
        )

    print(
        f"\nTotal Images Loaded: "
        f"{total_images}"
    )

    print("\n===================================\n")

    # ============================================
    # Safety Check
    # ============================================

    if len(class_counts) < 2:

        print(
            "\n[WARNING] Dataset contains "
            "fewer than 2 classes."
        )

        print(
            "SVM classification requires "
            "at least 2 classes.\n"
        )