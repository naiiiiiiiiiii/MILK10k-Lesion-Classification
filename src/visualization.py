import matplotlib.pyplot as plt
import numpy as np

def plot_image_grid(images, labels, cols=4, figsize=(12, 8)):
    """Plot grid of sample images with labels."""
    rows = int(np.ceil(len(images) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=figsize)
    axes = axes.flatten()
    
    for idx, (img, label) in enumerate(zip(images, labels)):
        # Rescale normalized z-score images to [0,1] for display visualization
        disp_img = img.copy()
        disp_img = (disp_img - disp_img.min()) / (disp_img.max() - disp_img.min() + 1e-7)
        
        axes[idx].imshow(disp_img)
        axes[idx].set_title(str(label))
        axes[idx].axis('off')
    
    plt.tight_layout()
    plt.show()

def plot_class_distribution(metadata_df, target_col='target'):
    """Plot class balance counts."""
    counts = metadata_df[target_col].value_counts()
    plt.figure(figsize=(8, 4))
    counts.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('Class Distribution')
    plt.xlabel('Diagnosis')
    plt.ylabel('Count')
    plt.show()

def plot_batch_diagnostics(raw_imgs, processed_imgs):
    """Side-by-side visual and distribution check."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    axes[0].imshow(cv2.cvtColor(raw_imgs[0], cv2.COLOR_BGR2RGB))
    axes[0].set_title("Raw Image")
    
    p_img = processed_imgs[0]
    p_disp = (p_img - p_img.min()) / (p_img.max() - p_img.min() + 1e-7)
    axes[1].imshow(p_disp)
    axes[1].set_title("Processed Image")
    
    axes[2].hist(processed_imgs.flatten(), bins=50, color='purple', alpha=0.7)
    axes[2].set_title("Processed Pixel Value Range")
    plt.show()