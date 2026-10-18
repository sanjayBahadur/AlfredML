from fastapi.testclient import TestClient
from alfred_ml.server import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "ollama_connected" in data
    assert "active_model" in data


def test_config_endpoint():
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()
    assert "docs_dir" in data
    assert "collection_name" in data
    assert "chunk_size" in data
    assert "top_k" in data


def test_ask_empty_question():
    response = client.post("/ask", json={"question": "   "})
    assert response.status_code == 400
