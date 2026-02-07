from app.processor import DataProcessor
import os
import structlog

# Setup Logging (JSON for Cloud Analysis)
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
log = structlog.get_logger()

def run_pilot_extraction():
    processor = DataProcessor()
    input_file = "input.pdf"
    output_file = "cleaned_work_report.xlsx"
    
    log.info("worker_started")
    
    if not os.path.exists(input_file):
        log.error("critical_error", reason="input_file_missing")
        return

    # 1. รันการสกัดข้อมูลแบบเข้มงวด
    df = processor.process_pdf_strictly(input_file)
    
    if df is not None and not df.empty:
        # 2. บันทึกผลลัพธ์
        processor.save_final_result(df, output_file)
        log.info("pilot_run_success", records=len(df))
    else:
        # 3. นโยบายลบไฟล์ขยะ
        log.warning("no_quality_data_found", action="deleting_junk_input")
        os.remove(input_file)

if __name__ == "__main__":
    run_pilot_extraction()
