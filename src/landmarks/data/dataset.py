from datasets import load_dataset
from torch.utils.data import Dataset
import torch

def load_metadata():
    hf_dataset = load_dataset("pemujo/GLDv2_Top_51_Categories")
    return hf_dataset

class LandmarkDataset(Dataset):
    def __init__(self, hf_split, transform=None, label_map=None):
        self.data = hf_split
        self.transform = transform

        if label_map is None:
            unique_labels = sorted(set(hf_split["label"]))
            self.label_map = {orig: idx for idx, orig in enumerate(unique_labels)}
        else:
            self.label_map = label_map

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        image = item["image"].convert("RGB")
        label = self.label_map[item["label"]]

        if self.transform:
            image = self.transform(image)

        return image, torch.tensor(label, dtype=torch.long)
    