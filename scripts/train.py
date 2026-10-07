import torch
import torch.optim as optim
from torch.utils.data import DataLoader

from src.models.landmark_model import build_model
from src.data.transforms import get_transforms
from src.data.dataset import LandmarkDataset, load_metadata
from src.training.train import run_model


def get_device():
    return torch.device(
        "cuda" if torch.cuda.is_available()
        else "mps" if torch.backends.mps.is_available()
        else "cpu"
    )


def main():
    ### get device
    device = get_device()
    print("Using device:", device)

    ### load in data / metadata
    hf_dataset = load_metadata()

    train_transform, val_transform = get_transforms()

    ### make dataset objects
    train_dataset = LandmarkDataset(hf_dataset["train"], transform=train_transform)
    val_dataset = LandmarkDataset(
        hf_dataset["test"],
        transform=val_transform,
        label_map=train_dataset.label_map
    )

    ### get dataloaders for datasets
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True, num_workers=2)
    val_loader   = DataLoader(val_dataset, batch_size=64, shuffle=False, num_workers=2)

    print("Train batches:", len(train_loader))
    print("Val batches:", len(val_loader))

    ### make the model
    num_classes = len(train_dataset.label_map)
    model = build_model(num_classes, unfreeze_layer4=True).to(device)

    optimizer = optim.Adam(model.parameters(), lr=5e-5)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)
    criterion = torch.nn.CrossEntropyLoss()

    ### train model
    run_model(model, train_loader, val_loader, criterion, optimizer, scheduler, device, epochs=10)


if __name__ == "__main__":
    main()