import cv2
import numpy as np

def preprocess_image(image_input, target_size=(224, 224), color_space='RGB', norm_type='z_score'):
    """
    Preprocesses a single image: loads/converts, resizes, and normalizes.
    Returns the processed image array and execution metadata.
    """
    # 1. Load image if file path is provided
    if isinstance(image_input, str):
        img = cv2.imread(image_input)
        if img is None:
            raise FileNotFoundError(f"Could not load image at path: {image_input}")
    else:
        img = image_input.copy()

    # 2. Color space conversion
    if color_space == 'RGB':
        if len(img.shape) == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    elif color_space == 'GRAY':
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = np.expand_dims(img, axis=-1)

    # 3. Resize image
    img_resized = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
    if len(img_resized.shape) == 2:
        img_resized = np.expand_dims(img_resized, axis=-1)

    # 4. Normalization
    img_float = img_resized.astype(np.float32)
    if norm_type == 'min_max':
        processed_img = img_float / 255.0
    elif norm_type == 'z_score':
        mean = np.mean(img_float)
        std = np.std(img_float) + 1e-7  # Prevent division by zero
        processed_img = (img_float - mean) / std
    else:
        processed_img = img_float

    metadata = {
        'shape': processed_img.shape,
        'dtype': processed_img.dtype,
        'min': float(np.min(processed_img)),
        'max': float(np.max(processed_img)),
        'norm_type': norm_type,
        'color_space': color_space
    }

    return processed_img, metadata


def process_image_batch(image_sources, target_size=(224, 224), color_space='RGB', norm_type='z_score'):
    """
    Processes a list/array of image paths or arrays in batch mode.
    Handles corrupt/missing files gracefully and returns a stacked array.
    """
    processed_images = []
    skipped_files = []

    for source in image_sources:
        try:
            img, _ = preprocess_image(source, target_size=target_size, color_space=color_space, norm_type=norm_type)
            processed_images.append(img)
        except Exception as e:
            skipped_files.append({'source': source, 'reason': str(e)})

    if skipped_files:
        print(f"[Warning] Skipped {len(skipped_files)} files due to processing errors.")

    if not processed_images:
        return np.array([]), skipped_files

    # Stack into shape: (N, H, W, C)
    batch_array = np.stack(processed_images, axis=0)
    return batch_array, skipped_files
