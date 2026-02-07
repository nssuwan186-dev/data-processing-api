from app.processor import DataProcessor
from app.security import DataPolicyEngine
import os
import structlog
import sys

# Setup Logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
log = structlog.get_logger()

def cloud_worker():
    """รันงานประมวลผลบน Cloud (GitHub Actions)"""
    job_type = os.getenv("JOB_TYPE", "process_pdf")
    processor = DataProcessor()
    policy_engine = DataPolicyEngine()
    
    log.info("cloud_worker_start", job=job_type)
    
    if job_type == "process_pdf":
        input_pdf = "input.pdf"
        if not os.path.exists(input_pdf):
            log.error("file_not_found", file=input_pdf)
            return

        # 1. สกัดและคัดกรองตาราง (ตัดคู่มือและคำอธิบายออก)
        clean_data = processor.process_pdf_smart_filter(input_pdf)
        
        if clean_data:
            # 2. บันทึกเฉพาะเนื้อหางานลง Excel
            output_file = "filtered_work_data.xlsx"
            processor.save_to_excel_clean(clean_data, output_file)
            log.info("processing_success", items=len(clean_data), output=output_file)
        else:
            # 3. ลบไฟล์ทิ้งถ้าเป็นไฟล์ว่างหรือมีแต่คู่มือ
            os.remove(input_pdf)
            log.warning("file_deleted", reason="empty_or_manual_only")
            
    else:
        log.info("other_job_types_not_implemented_in_pilot")

if __name__ == "__main__":
    cloud_worker()
