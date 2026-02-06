from app.processor import DataProcessor
from app.security import DataPolicyEngine
import os
import structlog

# Setup Logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
log = structlog.get_logger()

def main():
    job_type = os.getenv("JOB_TYPE", "process_excel")
    processor = DataProcessor()
    policy_engine = DataPolicyEngine()
    
    log.info("worker_start", job=job_type)
    
    if job_type == "process_pdf":
        # Example: สร้าง PDF รายงานที่มีข้อมูลองค์กร (Internal)
        content = "CONFIDENTIAL REPORT\n\nDepartment: IT Security\nStatus: All Systems Operational"
        processor.create_professional_pdf(content, filename="internal_report.pdf")
        
    elif job_type == "process_excel":
        # Example: ข้อมูลดิบที่มีทั้ง PII และข้อมูลทั่วไปปนกัน
        raw_data = [
            {"full_name": "Somchai Jai-dee", "email": "somchai@example.com", "phone_number": "0812345678", "national_id": "1103700123456"},
            {"full_name": "Jane Doe", "email": "jane.d@company.com", "phone_number": "0998887777"},
            {"org_name": "Tech Corp", "department": "Sales", "classification": "internal"},
            {"Item": "Server Cost", "Value": 50000} # ข้อมูลทั่วไปที่ไม่อยู่ใน Schema
        ]
        
        log.info("policy_enforcement_start", items=len(raw_data))
        
        # 1. คัดกรองและ Masking ข้อมูล
        clean_data = policy_engine.process_mixed_data(raw_data)
        
        # 2. ส่งข้อมูลที่สะอาดแล้วไปทำ Excel
        processor.process_excel_with_formulas(clean_data, filename="secure_summary.xlsx")
        
    else:
        log.error("unknown_job_type", job=job_type)
        exit(1)

if __name__ == "__main__":
    main()
