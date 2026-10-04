"""
landmark_project/backend/scripts/export_onnx.py

Exports the fine-tuned ResNet-18 model weights to ONNX and verifies it against PyTorch.

Run it from backend/ (with best_model.pth at root (landmark_project/) downloaded from Hugging Face):
    python -m scripts.export_onnx --weights ../best_model.pth
    python -m scripts.export_onnx --weights ../best_model.pth --check 200
"""
import argparse
import json
import random
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch
from datasets import load_dataset
from torchvision import models, transforms

from app.inference import LandmarkClassifier

OUT_DIR = Path(__file__).resolve().parent.parent / "model"
HF_DATASET = "pemujo/GLDv2_Top_51_Categories"


# main() (in this file) produces train_split
# Reproduces the class order used when the current model was trained
# Has the same index order as LandmarkDataset.label_map: sorted original labels
# WILL BE REWRITTEN DURING TRAINING REWRITE:
# Replace this with the classes.json saved by the training run (one source of truth)
def build_class_names(train_split) -> list[str]:
    label_to_name = {}
    for label, name in zip(train_split["label"], train_split["category"]):
        label_to_name.setdefault(label, name)
    return [label_to_name[label] for label in sorted(label_to_name)]


# Turns raw weights at weights_path into a model that can evaluate against a tensor
# Assumes model is of resnet18 shape with a linear last layer and (num_classes)-many classes
def load_model(weights_path: str, num_classes: int) -> torch.nn.Module:
    model = models.resnet18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
    model.load_state_dict(torch.load(weights_path, map_location="cpu"))
    return model.eval()


# Turns pytorch model into a ONNX model and writes it as a .onnx file to (out_path)
def export_and_verify(model: torch.nn.Module, out_path: Path) -> None:
    dummy = torch.randn(1, 3, 224, 224)
    torch.onnx.export(
        model, (dummy,), str(out_path),
        input_names=["input"], output_names=["logits"], opset_version=18,
    )
    with torch.no_grad():
        expected = model(dummy).numpy()
    sess = ort.InferenceSession(str(out_path), providers=["CPUExecutionProvider"])
    actual = sess.run(None, {sess.get_inputs()[0].name: dummy.numpy()})[0]
    np.testing.assert_allclose(actual, expected, rtol=1e-3, atol=1e-4)
    print(f"[ok] Exported {out_path.name}; logits match PyTorch")


# train_split and test_split come from huggingface
def check_pipeline(model, clf, classes, train_split, test_split, n: int) -> None:
    ref_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    label_to_idx = {lbl: i for i, lbl in enumerate(sorted(set(train_split["label"])))}
    random.seed(0)
    idxs = random.sample(range(len(test_split)), min(n, len(test_split)))

    agree = correct = 0
    for i in idxs:
        item = test_split[i]
        img = item["image"]
        with torch.no_grad():
            torch_idx = model(ref_tf(img.convert("RGB")).unsqueeze(0)).argmax(1).item()
        onnx_name = clf.predict(img, top_k=1)[0]["label"]
        agree += classes[torch_idx] == onnx_name
        correct += classes[label_to_idx[item["label"]]] == onnx_name
    print(f"[ok] PyTorch vs ONNX pipeline top-1 agreement: {agree}/{len(idxs)}")
    print(f"[ok] ONNX pipeline accuracy on test sample: {correct}/{len(idxs)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--check", type=int, default=0,
                    help="number of test images for the end-to-end check")
    args = ap.parse_args()

    ds = load_dataset(HF_DATASET)
    classes = build_class_names(ds["train"])
    print(f"{len(classes)} classes, first three: {classes[:3]}")

    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "classes.json").write_text(json.dumps(classes, indent=2))

    model = load_model(args.weights, len(classes))
    onnx_path = OUT_DIR / "landmarks.onnx"
    export_and_verify(model, onnx_path)

    clf = LandmarkClassifier(onnx_path, OUT_DIR / "classes.json")
    if args.check:
        check_pipeline(model, clf, classes, ds["train"], ds["test"], args.check)


if __name__ == "__main__":
    main()

#EOF