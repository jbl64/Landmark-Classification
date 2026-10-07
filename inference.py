import torch
from PIL import Image
from landmarks.models.landmark_model import build_model
from landmarks.data.transforms import get_transforms
from datasets import load_dataset

def load_label_map():
    ds = load_dataset("pemujo/GLDv2_Top_51_Categories", split="train")
    labels = sorted(set(ds["label"]))
    categories = {}
    for item in ds:
        if item["label"] not in categories:
            categories[item["label"]] = item["category"]
        if len(categories) == 51:
            break
    label_map = {idx: categories[orig] for idx, orig in enumerate(labels)}
    return label_map

def predict(image_path, weights_path="best_model.pth"):
    device = torch.device("cuda" if torch.cuda.is_available()
                          else "mps" if torch.backends.mps.is_available()
                          else "cpu")

    label_map = load_label_map()
    num_classes = len(label_map)

    model = build_model(num_classes, unfreeze_layer4=True).to(device)
    model.load_state_dict(torch.load(weights_path, map_location=device))
    model.eval()

    _, val_transform = get_transforms()
    image = Image.open(image_path).convert("RGB")
    x = val_transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)
        top5 = probs.topk(5)

    print(f"\nTop 5 predictions for: {image_path}")
    for prob, idx in zip(top5.values[0], top5.indices[0]):
        print(f"  {label_map[idx.item()]}: {prob.item():.2%}")

if __name__ == "__main__":
    import sys
    predict(sys.argv[1])