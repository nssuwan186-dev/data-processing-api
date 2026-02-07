from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.auth import get_current_user
from app.models import PersonalInfo, OrganizationInfo, DataClassification
from app.processor import DataProcessor
from app.security import DataPolicyEngine
from typing import List, Union
import structlog
import uvicorn
import os

# Setup Logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
log = structlog.get_logger()

# Initialize App
app = FastAPI(
    title="Data Processing Service",
    description="Enterprise-grade API for PDF & Excel processing with PII protection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS (Allow external access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Engines
processor = DataProcessor()
policy_engine = DataPolicyEngine()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "data-processing-api"}

@app.post("/process/excel", dependencies=[Depends(get_current_user)])
async def process_excel(data: List[dict], background_tasks: BackgroundTasks):
    """
    รับข้อมูล JSON -> ตรวจสอบ Policy -> สร้างไฟล์ Excel
    """
    log.info("api_request", endpoint="/process/excel", items=len(data))
    
    try:
        # 1. Apply Security Policy (Masking/Filtering)
        clean_data = policy_engine.process_mixed_data(data)
        
        # 2. Process File (Run in background if heavy)
        filename = "secure_output.xlsx"
        output_path = processor.process_excel_with_formulas(clean_data, filename=filename)
        
        return {
            "status": "success",
            "message": "Data processed and masked successfully",
            "output_file": str(output_path),
            "record_count": len(clean_data)
        }
    except Exception as e:
        log.error("processing_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/pdf", dependencies=[Depends(get_current_user)])
async def process_pdf(content: str, classification: DataClassification = DataClassification.INTERNAL):
    """
    สร้าง PDF Report ตามระดับความลับ
    """
    log.info("api_request", endpoint="/process/pdf", classification=classification)
    
    # Header stamping based on classification
    header_text = f"CONFIDENTIALITY LEVEL: {classification.upper()}"
    final_content = f"{header_text}\n\n{content}"
    
    try:
        filename = f"report_{classification}.pdf"
        output_path = processor.create_professional_pdf(final_content, filename=filename)
        
        return {
            "status": "success",
            "file_path": str(output_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # For local debugging
    uvicorn.run(app, host="0.0.0.0", port=8000)
