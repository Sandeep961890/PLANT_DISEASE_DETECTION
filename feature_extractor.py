import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import gc
import numpy as np
import tensorflow as tf

from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.applications.efficientnet import (
    preprocess_input as effpre
)

from typing import List, Tuple


# =========================================================
# ENABLE MEMORY GROWTH FOR GPU
# =========================================================

gpus = tf.config.list_physical_devices('GPU')

if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except Exception as e:
        print(e)


# =========================================================
# DEVICE INFORMATION
# =========================================================

def get_device_info():
    """
    Return TensorFlow device information.
    """

    gpus = tf.config.list_physical_devices('GPU')

    return {
        'tensorflow_version': tf.__version__,
        'num_gpus': len(gpus),
        'gpus': [gpu.name for gpu in gpus]
    }


# =========================================================
# LOAD EFFICIENTNET MODEL
# =========================================================

def build_model():
    """
    Build pretrained EfficientNetB0 model
    for deep feature extraction.
    """

    print("\n===================================")
    print(" LOADING EFFICIENTNETB0 ")
    print("===================================\n")

    model = EfficientNetB0(
        weights='imagenet',
        include_top=False,
        pooling='avg'
    )

    print("EfficientNetB0 Loaded Successfully\n")

    return model


# =========================================================
# FEATURE EXTRACTOR
# =========================================================

class FeatureExtractor:

    def __init__(self, batch_size: int = 32):

        self.batch_size = batch_size

        self.model = build_model()

    # =====================================================
    # FEATURE EXTRACTION FROM ARRAY
    # =====================================================

    def extract_from_array(
        self,
        imgs: np.ndarray
    ) -> np.ndarray:
        """
        Extract features from image arrays.
        """

        try:

            # Convert normalized images
            # back to pixel range
            imgs_px = (imgs * 255.0).astype(np.float32)

            # EfficientNet preprocessing
            imgs_pre = effpre(imgs_px)

            # Extract features
            features = self.model.predict(
                imgs_pre,
                batch_size=self.batch_size,
                verbose=0
            )

            return features

        except Exception as e:

            print("\n[ERROR] Feature extraction failed")
            print(e)

            return np.zeros(
                (0, self.model.output_shape[-1]),
                dtype=np.float32
            )

    # =====================================================
    # FEATURE EXTRACTION FROM PATHS
    # =====================================================

    def extract_from_paths(
        self,
        paths: List[str],
        labels: List[str],
        preprocess_fn
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Extract features from image file paths.

        Parameters:
        ----------
        paths : List[str]
            Image file paths

        labels : List[str]
            Corresponding labels

        preprocess_fn : function
            Image preprocessing function

        Returns:
        -------
        final_features : np.ndarray
            Extracted EfficientNet features

        valid_labels : List[str]
            Labels aligned with valid features
        """

        all_features = []

        valid_labels = []

        batch_images = []

        batch_labels = []

        total_images = len(paths)

        skipped_images = 0

        print("\n===================================")
        print(" FEATURE EXTRACTION STARTED ")
        print("===================================\n")

        print(f"Total Images: {total_images}\n")

        # =================================================
        # PROCESS EACH IMAGE
        # =================================================

        for idx, (path, label) in enumerate(zip(paths, labels)):

            try:

                # -----------------------------------------
                # PREPROCESS IMAGE
                # -----------------------------------------

                img = preprocess_fn(path)

                # Skip corrupted image
                if img is None:

                    skipped_images += 1

                    print(
                        f"[WARNING] Skipped corrupted image:\n{path}"
                    )

                    continue

                # Add image to batch
                batch_images.append(img)

                batch_labels.append(label)

                # -----------------------------------------
                # PROCESS BATCH
                # -----------------------------------------

                if len(batch_images) >= self.batch_size:

                    batch_array = np.stack(
                        batch_images,
                        axis=0
                    )

                    batch_features = self.extract_from_array(
                        batch_array
                    )

                    # Save features
                    all_features.append(batch_features)

                    # Save labels
                    valid_labels.extend(batch_labels)

                    print(
                        f"Processed: "
                        f"{min(idx + 1, total_images)}"
                        f"/{total_images}"
                    )

                    # Clear memory
                    batch_images.clear()
                    batch_labels.clear()

                    gc.collect()

            except Exception as e:

                skipped_images += 1

                print("\n[ERROR] Failed processing image")
                print(path)
                print(e)

        # =================================================
        # PROCESS REMAINING BATCH
        # =================================================

        if len(batch_images) > 0:

            try:

                batch_array = np.stack(
                    batch_images,
                    axis=0
                )

                batch_features = self.extract_from_array(
                    batch_array
                )

                all_features.append(batch_features)

                valid_labels.extend(batch_labels)

            except Exception as e:

                print("\n[ERROR] Failed processing final batch")
                print(e)

        # =================================================
        # HANDLE EMPTY OUTPUT
        # =================================================

        if len(all_features) == 0:

            print("\n[ERROR] No valid images found!")

            return (
                np.zeros(
                    (0, self.model.output_shape[-1]),
                    dtype=np.float32
                ),
                []
            )

        # =================================================
        # COMBINE FEATURES
        # =================================================

        final_features = np.vstack(all_features)

        # =================================================
        # SUMMARY
        # =================================================

        print("\n===================================")
        print(" FEATURE EXTRACTION COMPLETED ")
        print("===================================\n")

        print(f"Total Images       : {total_images}")
        print(f"Valid Images       : {len(valid_labels)}")
        print(f"Skipped Images     : {skipped_images}")

        print(f"\nFeature Shape      : {final_features.shape}")

        print(
            f"Feature Vector Size: "
            f"{final_features.shape[1]}"
        )

        print("\n===================================\n")

        return final_features, valid_labels
    # =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("\nDEVICE INFO:")
    print(get_device_info())

    extractor = FeatureExtractor()

    print("\nFeatureExtractor initialized successfully!")