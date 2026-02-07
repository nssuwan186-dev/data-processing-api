from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "data-processing-api"}

def test_excel_processing_unauthorized():
    # ไม่ส่ง API Key ต้องเจอ 403
    response = client.post("/process/excel", json=[])
    assert response.status_code == 403

def test_excel_processing_success():
    # ส่ง API Key และข้อมูลทดสอบ
    headers = {"X-API-Key": "dev-secret-key-123"}
    payload = [
        {"full_name": "Test User", "email": "test@example.com", "phone_number": "0812345678"}
    ]
    
    response = client.post("/process/excel", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "secure_output.xlsx" in data["output_file"]

def test_pdf_processing():
    headers = {"X-API-Key": "dev-secret-key-123"}
    response = client.post(
        "/process/pdf?classification=confidential", 
        json="This is a test report", # Body should be string for this endpoint wrapper, wait.. 
        # Fastapi handles body parsing. In main.py: content: str. 
        # Let's fix the call to match expected input usually query or body.
        # Simple fix: pass as query for simplicity or fix main.py to take body model.
        # Actually main.py takes `content: str` which usually implies query param if not Body().
        # Let's adjust test to pass query param for content to be safe with default FastAPI behavior for scalars
        params={"content": "Test Report Content"},
        headers=headers
    )
    assert response.status_code == 200
    assert "report_confidential.pdf" in response.json()["file_path"]
