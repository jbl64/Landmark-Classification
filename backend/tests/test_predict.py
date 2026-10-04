"""
landmark_project/backend/tests/test_predict.py
Dev environment testing

Run from backend/ with:
"python -m pytest tests/test_predict.py"
"""
import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import MAX_UPLOAD_BYTES, app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def make_image_bytes(mode="RGB", fmt="PNG"):
    buf = io.BytesIO()
    Image.new(mode, (64, 64)).save(buf, format=fmt)
    return buf.getvalue()


def post_file(client, content, filename="test.png", content_type="image/png"):
    return client.post("/predict", files={"file": (filename, content, content_type)})


def test_predict_valid_image(client):
    response = post_file(client, make_image_bytes())
    assert response.status_code == 200
    predictions = response.json()["predictions"]
    assert len(predictions) == 3
    confidences = [p["confidence"] for p in predictions]
    assert all(isinstance(p["label"], str) for p in predictions)
    assert all(0.0 <= c <= 1.0 for c in confidences)
    assert confidences == sorted(confidences, reverse=True)


def test_predict_rgba_and_grayscale(client):
    for mode in ("RGBA", "L"):
        response = post_file(client, make_image_bytes(mode=mode))
        assert response.status_code == 200


def test_predict_not_an_image(client):
    response = post_file(client, b"this is not an image", "notes.txt", "text/plain")
    assert response.status_code == 400


def test_predict_too_large(client):
    response = post_file(client, b"0" * (MAX_UPLOAD_BYTES + 1))
    assert response.status_code == 413


def test_predict_missing_file(client):
    response = client.post("/predict")
    assert response.status_code == 422

#EOF