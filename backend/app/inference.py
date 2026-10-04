"""
landmark_project/backend/app/inference.py

Here lives the NN logic and class definition used in main
(landmark_project/backend/app/main.py)
"""

import json
from pathlib import Path
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageOps


# The valeus below must match their corresponding values from transforms.py
# (landmark_project/src/data/transforms.py)
# The transformation is a squash with no image cropping
# Helper for LandmarkClassifier's predict method
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)
SIZE = 224


# Code for preprocesing an input image (img)
# Transforms it into a numpy array the NN model in LandmarksClassifier understands
# Helper for LandmarkClassifier's predict method
def preprocess(img: Image.Image) -> np.ndarray:
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")
    img = img.resize((SIZE, SIZE), resample=Image.BILINEAR)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = (arr - MEAN) / STD
    arr = arr.transpose(2, 0, 1)
    arr = arr[np.newaxis, ...]
    return arr


# Transforms logits (raw output of NN MODEL) into probabilities
def softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - np.max(logits)
    exps = np.exp(shifted)
    return exps / np.sum(exps)


# Class that classifies an image
# NOTES:
# 1. __init__ takes in the path to the NN model and index of classes
# 2. predict method takes in raw img
class LandmarkClassifier:
    def __init__(self, model_path: Path, classes_path: Path):
        self.session = ort.InferenceSession(
            str(model_path), providers=["CPUExecutionProvider"]
        )
        self.input_name = self.session.get_inputs()[0].name
        with open(classes_path) as f:
            self.classes = json.load(f)

    # returns top (top_k)-many predictions
    # takes IMG image (img) as input 
    def predict(self, img: Image.Image, top_k: int = 3) -> list[dict]:
        x = preprocess(img)
        logits = self.session.run(None, {self.input_name: x})[0][0]
        probs = softmax(logits)
        top = np.argsort(probs)[::-1][:top_k]
        return [
            {"label": self.classes[i], "confidence": float(probs[i])}
            for i in top
        ]


#EOF