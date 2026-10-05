# Landmark Classifier

Upload a photo of a landmark and the model guesses which of 51 famous landmarks it is.

- [LIVE DEMO](https://landmark-classification.vercel.app)
- [Dataset](https://huggingface.co/datasets/pemujo/GLDv2_Top_51_Categories)
- [Model weights](https://huggingface.co/jblee64/landmark-classification-resnet18)

NOTE: The backend runs on Render, which sleeps when idle, so the first visit can take a while to load.

## How it works

The page is a React app served by Vercel. When you upload a photo, your browser sends it to a FastAPI service on Render, which runs the model and returns the top three guesses with confidence scores.

The model is a ResNet-18, pretrained on ImageNet and fine-tuned in PyTorch on 51 landmark classes. For serving, it is exported to ONNX and checked against the PyTorch version, so the server runs without PyTorch.

See [`backend/README.md`](backend/README.md) and [`frontend/README.md`](frontend/README.md) for details.

## Results

95.2% validation accuracy on the 51-class [GLDv2 subset](https://huggingface.co/datasets/pemujo/GLDv2_Top_51_Categories), about 36k images.

## Tech stack

PyTorch, ONNX Runtime, FastAPI, React, Vite, Render, Vercel.

## Running it locally

The backend and frontend each have their own setup. See [`backend/README.md`](backend/README.md) and [`frontend/README.md`](frontend/README.md).

The training code is in `src/` (`python -m src.main`). The original command-line script for the PyTorch weights is `inference.py` in the repo root.

## Limitations

- The first request after a period of inactivity can take a while, since the free server has to wake up and load the model.
- The model only knows 51 landmarks. Its confidence is relative to those 51, so a photo of anything else still gets confident-looking labels. 
- The public demo has no authentication.

## What's next

(in no particular order)
- Reworking the training pipeline
- Expanding the dataset to cover more landmarks

This is the first stage of a project to build an agent that can play [TimeGuessr](https://timeguessr.com).