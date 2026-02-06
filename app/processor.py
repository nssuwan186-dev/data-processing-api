import pandas as pd
import fitz  # PyMuPDF
from openpyxl.styles import Font, Alignment
from pathlib import Path
import structlog

log = structlog.get_logger()

class DataProcessor:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def process_excel_with_formulas(self, data: list, filename: str = "summary.xlsx"):
        """จัดการข้อมูล Excel พร้อมใส่สูตรและจัดรูปแบบ"""
        log.info("excel_processing_start", filename=filename)
        df = pd.DataFrame(data)
        path = self.output_dir / filename
        
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
            workbook = writer.book
            worksheet = writer.sheets['Data']
            
            # ใส่สูตรคำนวณอัตโนมัติ (เช่น ผลรวมที่แถวสุดท้าย)
            last_row = len(df) + 1
            worksheet[f'A{last_row + 1}'] = 'TOTAL'
            worksheet[f'B{last_row + 1}'] = f'=SUM(B2:B{last_row})'
            
            # จัดรูปแบบ
            cell = worksheet[f'A{last_row + 1}']
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')
            
        log.info("excel_processing_complete", path=str(path))
        return path

    def extract_pdf_content(self, pdf_path: str):
        """อ่านและตรวจสอบเนื้อหาใน PDF"""
        log.info("pdf_extraction_start", path=pdf_path)
        content = []
        with fitz.open(pdf_path) as doc:
            for page in doc:
                content.append(page.get_text())
        
        log.info("pdf_extraction_complete", pages=len(content))
        return "\n".join(content)

    def create_professional_pdf(self, text: str, filename: str = "report.pdf"):
        """สร้างไฟล์ PDF ใหม่ตามมาตรฐาน"""
        log.info("pdf_creation_start", filename=filename)
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), text, fontsize=12)
        
        path = self.output_dir / filename
        doc.save(path)
        log.info("pdf_creation_complete", path=str(path))
        return path
