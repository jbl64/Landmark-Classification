# Backend

Here lives the FastAPI service that classifies landmark photos with an ONNX model. It serves the ResNet-18 trained model that lives in the repo root. Note that it runs without PyTorch.

Live backend API: `https://landmark-classification.onrender.com` (docs at `/docs`)

## Layout

```
backend/
  app/
    inference.py       preprocessing, softmax, and the LandmarkClassifier class
    main.py            the FastAPI app (/health and /predict)
  scripts/
    export_onnx.py     converts best_model.pth to ONNX and verifies it
  model/               landmarks.onnx, landmarks.onnx.data, classes.json (committed)
  tests/
    test_predict.py    API tests
  requirements.txt         what the server needs (this is what Render installs)
  requirements-export.txt  laptop-only extras: torch, torchvision, datasets, pytest
```

`app/inference.py` here is different from the `inference.py` in the repo root. The former is the lightweight class the backend app uses. The latter is the original command-line script for the PyTorch weights.

## Setup

From the repo root:

```bash
python -m venv .venv --prompt landmark
source .venv/bin/activate
cd backend
pip install -r requirements-export.txt
```

Developed on Python 3.13.13.

Run every command below from `backend/` with the venv active.

## Exporting the model

The server loads `model/landmarks.onnx` and `model/classes.json`, both committed to the repo. You only need to re-export if the model or the class list changes.

1. Download `best_model.pth` from [jblee64/landmark-classification-resnet18](https://huggingface.co/jblee64/landmark-classification-resnet18) into the repo root. It is git-ignored.
2. Export and check:

```bash
python -m scripts.export_onnx --weights ../best_model.pth --check 200
```

Without `--check`, the script exports and compares the ONNX output with PyTorch on one random input. With `--check N`, it also runs N real test images through both the training-style pipeline (torchvision and PyTorch) and the server pipeline (`preprocess` and ONNX), and prints how often their top-1 predictions agree. Agreement should be nearly 100%, and a low number means the two preprocessing paths differ.

The script writes `model/landmarks.onnx`, `model/classes.json`, and possibly `model/landmarks.onnx.data`. The order of classes comes from the dataset's sorted labels and has to match the order used in training. If the class list changes, re-export it so that `classes.json` and the model stay aligned.

## Running the server locally

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/health`, or `http://127.0.0.1:8000/docs` to try `/predict` from the browser.

## Testing

```bash
python -m pytest tests/test_predict.py
```

The tests use FastAPI's `TestClient`, which runs the app inside pytest with the real model loaded. They cover a health check, a valid image, RGBA and grayscale inputs, a non-image file, an oversized file, and a missing file.

## API

### `GET /health`

Returns `{"status": "ok"}`. IMPORTANT TO NOTE: The frontend calls it on the initial page load so that the sleeping server (Render) starts waking up before the user picks a photo.

### `POST /predict`

Takes a multipart upload with the image in a field named `file`. Returns the top three predictions, highest first:

Errors:

| Status | Meaning |
|---|---|
| 400 | The file is not a valid image |
| 413 | The file is larger than 10 MB |
| 422 | No `file` field in the request (FastAPI's own validation) |

Any image format Pillow can decode works. Before classification, the image gets its EXIF rotation applied, is converted to RGB, is squashed to 224 x 224 with no cropping, and is normalized with the ImageNet mean and standard deviation. These must match `src/data/transforms.py` in the repo root.

Confidence is how the model splits its probability across the 51 known landmarks. It is not a measure of whether the photo shows one of them, so an unrelated photo still gets confident-looking labels.

## CORS Configuration

`ALLOWED_ORIGINS` sets which frontends the browser may call this API from CORS. CORS is enforced by browsers only. It does not restrict other clients such as curl, and the API has no authentication.

```
ALLOWED_ORIGINS=https://landmark-classification.vercel.app,http://localhost:5173
```

## Deploying to Render

Create a Web Service connected to the repo, with these settings:

| Setting | Value |
|---|---|
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Environment | `ALLOWED_ORIGINS`, and `PYTHON_VERSION` to match your local Python |

`requirements.txt` has no torch, so the build stays small. On Render's free tier, the service spins down after about 15 minutes without traffic, and the next request waits while it restarts and loads the model.