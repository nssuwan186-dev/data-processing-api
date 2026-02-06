import os
import structlog
import pandas as pd
import fitz  # PyMuPDF
from pathlib import Path

# Setup Logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
log = structlog.get_logger()

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def process_pdf():
    log.info("task_started", task="pdf_processing")
    # Simulation: Create a dummy PDF
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Processed by GitHub Actions Cloud Runner", fontsize=20)
    
    output_path = OUTPUT_DIR / "report.pdf"
    doc.save(output_path)
    log.info("task_completed", file=str(output_path))

def process_excel():
    log.info("task_started", task="excel_processing")
    # Simulation: Create an Excel with formula
    df = pd.DataFrame({'Data': [10, 20, 30, 40]})
    
    output_path = OUTPUT_DIR / "summary.xlsx"
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        worksheet = writer.sheets['Sheet1']
        worksheet['A6'] = 'Total'
        worksheet['B6'] = '=SUM(A2:A5)'
        
    log.info("task_completed", file=str(output_path))

def main():
    job_type = os.getenv("JOB_TYPE", "process_pdf")
    log.info("worker_start", job=job_type)
    
    if job_type == "process_pdf":
        process_pdf()
    elif job_type == "process_excel":
        process_excel()
    else:
        log.error("unknown_job_type", job=job_type)
        exit(1)

if __name__ == "__main__":
    main()
