import sys
import os
import numpy as np

# Ensure Python can locate the src directory
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.preprocessing import preprocess_image, process_image_batch

print("--- TESTING PREPROCESSING MODULE ---")

# 1. Test single synthetic image preprocessing
dummy_img = np.random.randint(0, 256, (300, 300, 3), dtype=np.uint8)
processed_img, meta = preprocess_image(dummy_img, target_size=(224, 224), norm_type='z_score')

print(f"Original shape: (300, 300, 3)")
print(f"Processed shape: {processed_img.shape}")
print(f"Processed min/max: {meta['min']:.2f} / {meta['max']:.2f}")
print(f"Norm type: {meta['norm_type']}")

# 2. Test batch processing
dummy_batch = [dummy_img, dummy_img]
batch_array, skipped = process_image_batch(dummy_batch, target_size=(224, 224))
print(f"Batch array shape: {batch_array.shape}")
print(f"Skipped files count: {len(skipped)}")

print("\nSuccess! Preprocessing module is working.")
