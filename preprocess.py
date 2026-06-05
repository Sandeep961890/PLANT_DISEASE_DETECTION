import os
import cv2
import numpy as np
from typing import Tuple, Optional, Generator


def read_image_safe(path: str) -> Optional[np.ndarray]:
    """
    Safely read image from disk.

    Supports:
    - Unicode file paths
    - Corrupted image handling
    - Windows-compatible loading
    """

    try:

        img = cv2.imdecode(
            np.fromfile(path, dtype=np.uint8),
            cv2.IMREAD_COLOR
        )

        if img is None:
            print(f"[WARNING] Unable to read image: {path}")
            return None

        return img

    except Exception as e:

        print(f"[ERROR] Failed reading image: {path}")
        print(e)

        return None


def clahe_enhance(img: np.ndarray) -> np.ndarray:
    """
    Apply CLAHE enhancement to improve
    leaf texture and disease visibility.
    """

    # Convert BGR to LAB color space
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

    # Split channels
    l, a, b = cv2.split(lab)

    # CLAHE on Lightness channel
    clahe = cv2.createCLAHE(
        clipLimit=3.0,
        tileGridSize=(8, 8)
    )

    cl = clahe.apply(l)

    # Merge channels
    merged = cv2.merge((cl, a, b))

    # Convert back to BGR
    enhanced = cv2.cvtColor(
        merged,
        cv2.COLOR_LAB2BGR
    )

    return enhanced


def preprocess_image(
    path: str,
    size: Tuple[int, int] = (224, 224)
) -> Optional[np.ndarray]:
    """
    Complete preprocessing pipeline.

    Steps:
    1. Safe image loading
    2. Noise reduction
    3. CLAHE enhancement
    4. RGB conversion
    5. Resize
    6. Normalization
    """

    # Read image safely
    img = read_image_safe(path)

    if img is None:
        return None

    try:

        # Noise reduction
        img = cv2.GaussianBlur(img, (3, 3), 0)

        # CLAHE enhancement
        img = clahe_enhance(img)

        # Convert BGR → RGB
        img = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2RGB
        )

        # Resize image
        img = cv2.resize(
            img,
            size,
            interpolation=cv2.INTER_AREA
        )

        # Normalize pixels
        img = img.astype(np.float32) / 255.0

        return img

    except Exception as e:

        print(f"[ERROR] Failed preprocessing image: {path}")
        print(e)

        return None


def load_dataset_paths(
    root_dir: str
) -> Generator[Tuple[str, str], None, None]:
    """
    Load dataset image paths and labels.

    Expected Structure:
    dataset/
        healthy/
        diseased/

    Returns:
    --------
    Generator:
        (image_path, class_label)
    """

    if not os.path.exists(root_dir):

        raise FileNotFoundError(
            f"Dataset directory not found: {root_dir}"
        )

    # Get class folders
    classes = []

    for entry in sorted(os.listdir(root_dir)):

        class_path = os.path.join(root_dir, entry)

        if os.path.isdir(class_path):
            classes.append(entry)

    print(f"\nFound Classes: {classes}\n")

    # Supported image formats
    valid_extensions = (
        '.jpg',
        '.jpeg',
        '.png',
        '.bmp',
        '.tif',
        '.tiff',
        '.webp'
    )

    # Traverse class folders
    for cls in classes:

        cls_dir = os.path.join(root_dir, cls)

        image_count = 0

        for fname in os.listdir(cls_dir):

            if fname.lower().endswith(valid_extensions):

                image_path = os.path.join(cls_dir, fname)

                image_count += 1

                yield image_path, cls

        print(f"[INFO] Loaded {image_count} images from class: {cls}")