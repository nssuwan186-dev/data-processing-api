import pandas as pd
import fitz
from pathlib import Path
import structlog
import os

log = structlog.get_logger()

class DataProcessor:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        # คีย์เวิร์ดที่ต้องมีใน "เนื้อหางาน"
        self.work_anchors = ["ลำดับ", "รายการ", "งาน", "สถานะ", "ผู้รับผิดชอบ", "วันที่"]

    def is_real_work_page(self, page):
        """ตรวจสอบว่าหน้านี้มีเนื้อหางานจริงๆ หรือไม่"""
        text = page.get_text().lower()
        # 1. ต้องมี Anchor keywords อย่างน้อย 2 คำ
        matches = sum(1 for anchor in self.work_anchors if anchor in text)
        if matches < 2:
            return False
        
        # 2. ต้องมีโครงสร้างตาราง
        tabs = page.find_tables()
        return len(tabs.tables) > 0

    def process_pdf_strictly(self, pdf_path: str):
        """สกัดข้อมูลแบบเน้นคุณภาพ (Quality-First)"""
        log.info("strict_processing_start", file=pdf_path)
        all_data = []
        
        with fitz.open(pdf_path) as doc:
            for i, page in enumerate(doc):
                if not self.is_real_work_page(page):
                    log.info("skipping_junk_page", page=i+1)
                    continue
                
                tabs = page.find_tables()
                for tab in tabs:
                    df = tab.to_pandas()
                    # ลบแถว/คอลัมน์ที่ว่างเปล่าทิ้งทันที (Cleanup)
                    df = df.dropna(how='all').dropna(how='all', axis=1)
                    if not df.empty:
                        all_data.append(df)
        
        if not all_data:
            return None
            
        # รวมข้อมูลทุกหน้าเป็นตารางเดียว
        final_df = pd.concat(all_data, ignore_index=True)
        return final_df

    def save_final_result(self, df, filename: str):
        path = self.output_dir / filename
        df.to_excel(path, index=False)
        log.info("data_saved_successfully", path=str(path))
        return path
