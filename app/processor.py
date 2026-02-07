import pandas as pd
import fitz  # PyMuPDF
from openpyxl.styles import Font, Alignment
from pathlib import Path
import structlog
import re

log = structlog.get_logger()

class DataProcessor:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        # Keywords ที่บ่งบอกว่าเป็น "คู่มือ" หรือ "คำอธิบาย" (ไม่ใช่เนื้อหางาน)
        self.blacklist_keywords = ["คู่มือ", "แนวทาง", "วิธีใช้งาน", "คำชี้แจง", "หมายเหตุ", "ขั้นตอนการ", "manual", "guide"]

    def is_tabular_data(self, text: str):
        """ตรวจสอบว่าข้อความมีลักษณะเป็นตารางหรือเนื้อหางานหรือไม่"""
        # ถ้าข้อความมีความยาวมากเกินไปในย่อหน้าเดียว มักจะเป็น "คำอธิบาย"
        if len(text) > 500 and "\n" not in text[:100]:
            return False
        
        # ตรวจสอบ Blacklist keywords
        if any(kw in text for kw in self.blacklist_keywords):
            return False
            
        return True

    def process_pdf_smart_filter(self, pdf_path: str):
        """อ่าน PDF และกรองเอาเฉพาะข้อมูลตาราง/เนื้อหางาน"""
        log.info("smart_filter_start", path=pdf_path)
        extracted_rows = []
        
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc):
                # 1. ดึงตารางจากหน้า (ถ้ามี)
                tabs = page.find_tables()
                if tabs.tables:
                    for tab in tabs:
                        df = tab.to_pandas()
                        # กรองคอลัมน์ที่ว่างเปล่าออก
                        df = df.dropna(how='all', axis=1)
                        # เพิ่มข้อมูลเข้า list
                        extracted_rows.extend(df.to_dict(orient='records'))
                    log.info("table_extracted", page=page_num + 1)
                else:
                    # 2. ถ้าไม่มีโครงสร้างตารางแบบชัดเจน ให้ลองวิเคราะห์ข้อความ
                    text = page.get_text()
                    if self.is_tabular_data(text):
                        # พยายามแบ่งแถวด้วยบรรทัด
                        lines = [line.strip() for line in text.split("\n") if line.strip()]
                        if len(lines) > 2: # ต้องมีหลายบรรทัดถึงจะนับเป็นข้อมูล
                            extracted_rows.append({"raw_content": text, "page": page_num + 1})
        
        if not extracted_rows:
            log.warning("no_relevant_data_found", path=pdf_path)
            return None

        log.info("smart_filter_complete", total_records=len(extracted_rows))
        return extracted_rows

    def save_to_excel_clean(self, data: list, filename: str):
        """บันทึกเฉพาะข้อมูลที่คัดกรองแล้วลง Excel"""
        if not data: return None
        
        path = self.output_dir / filename
        df = pd.DataFrame(data)
        
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='WorkContent')
            # ตกแต่งหัวตารางให้เป็นมืออาชีพ
            ws = writer.sheets['WorkContent']
            for cell in ws[1]:
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center')
                
        return path
