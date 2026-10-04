import os
import pandas as pd
import numpy as np
from src.preprocessing import preprocess_batch

class MILK10kDataLoader:
    def __init__(self, metadata_path, img_dir, batch_size=32, target_size=(224, 224), shuffle=True):
        self.metadata = pd.read_csv(metadata_path)
        self.img_dir = img_dir
        self.batch_size = batch_size
        self.target_size = target_size
        self.shuffle = shuffle
        
        # Part 4 Requirement: Filter locally available files only
        self.metadata['full_path'] = self.metadata['image_id'].apply(lambda x: os.path.join(img_dir, f"{x}.jpg"))
        self.valid_df = self.metadata[self.metadata['full_path'].apply(os.path.exists)].reset_index(drop=True)
        self.indices = np.arange(len(self.valid_df))

    def __len__(self):
        return int(np.ceil(len(self.valid_df) / self.batch_size))

    def __iter__(self):
        if self.shuffle:
            np.random.shuffle(self.indices)
        
        for i in range(0, len(self.valid_df), self.batch_size):
            batch_idx = self.indices[i:i + self.batch_size]
            batch_rows = self.valid_df.iloc[batch_idx]
            
            paths = batch_rows['full_path'].tolist()
            labels = batch_rows['target'].values
            
            images, skipped = preprocess_batch(paths, target_size=self.target_size)
            yield images, labels