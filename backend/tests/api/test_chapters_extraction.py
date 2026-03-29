import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_extract_entities_endpoint_exists():
    """测试端点存在"""
    response = client.post("/api/chapters/1/extract-entities")
    # 应该返回 401 或 404，但不应该是 404（路由不存在）
    assert response.status_code != 404
