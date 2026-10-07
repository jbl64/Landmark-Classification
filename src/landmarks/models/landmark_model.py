import torch.nn as nn
from torchvision.models import resnet18, ResNet18_Weights

def build_model(num_classes, unfreeze_layer4=False):
    weights = ResNet18_Weights.DEFAULT
    model = resnet18(weights=weights)

    for param in model.parameters():
        param.requires_grad = False

    if unfreeze_layer4:
        for param in model.layer4.parameters():
            param.requires_grad = True

    model.fc = nn.Linear(model.fc.in_features, num_classes)

    return model