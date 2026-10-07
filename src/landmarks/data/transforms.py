from torchvision import transforms
from torchvision.models import ResNet18_Weights

### returns image transforms for training and testing datasets
def get_transforms():
    weights = ResNet18_Weights.DEFAULT

    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=weights.transforms().mean,
            std=weights.transforms().std
        )
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=weights.transforms().mean,
            std=weights.transforms().std
        )
    ])

    return train_transform, val_transform