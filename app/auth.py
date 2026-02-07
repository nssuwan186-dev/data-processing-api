from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os
import structlog

log = structlog.get_logger()

# กำหนดชื่อ Header ที่ต้องส่งมา เช่น X-API-Key: mysecretkey
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_current_user(api_key_header: str = Security(api_key_header)):
    """
    Validate API Key from request header.
    In production, replace this with Database lookup or JWT validation.
    """
    # ดึงค่าจาก ENV หรือใช้ Default สำหรับ Dev
    EXPECTED_API_KEY = os.getenv("SERVICE_API_KEY", "dev-secret-key-123")

    if api_key_header == EXPECTED_API_KEY:
        return {"username": "admin", "role": "system_admin"}
    
    log.warning("auth_failed", provided_key=api_key_header[:3] + "***" if api_key_header else "None")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
    )
