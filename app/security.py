import re
from app.models import DataClassification, PersonalInfo, OrganizationInfo

class DataPolicyEngine:
    def __init__(self):
        # Regex สำหรับจับ Pattern ข้อมูลละเอียดอ่อน (เช่น บัตร ปชช., เบอร์โทร)
        self.email_regex = r'[\w\.-]+@[\w\.-]+\.\w+'
        self.phone_regex = r'(\d{3})[-.]?(\d{3})[-.]?(\d{4})'

    def mask_string(self, text: str, visible_chars: int = 2) -> str:
        """Helper function to mask strings like '123456' -> '12****'"""
        if not text or len(text) <= visible_chars:
            return text
        return text[:visible_chars] + "*" * (len(text) - visible_chars)

    def sanitize_personal_data(self, person: PersonalInfo) -> dict:
        """
        บังคับใช้นโยบายกับข้อมูลส่วนบุคคล:
        - ถ้าเป็น Confidential -> ต้องปิดบังเบอร์โทรและอีเมลบางส่วน
        - ถ้าเป็น Restricted -> ต้องปิดบังทั้งหมด
        """
        data = person.model_dump()
        
        if person.classification in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]:
            # Masking logic
            data['phone_number'] = self.mask_string(person.phone_number, 3) # 081*******
            
            if '@' in data['email']:
                user, domain = data['email'].split('@')
                data['email'] = f"{self.mask_string(user, 2)}@{domain}"
            
            if person.national_id:
                data['national_id'] = "REDACTED" # ไม่เก็บลงไฟล์ผลลัพธ์เด็ดขาด

        return data

    def validate_corporate_access(self, org: OrganizationInfo, requester_level: DataClassification) -> bool:
        """
        ตรวจสอบสิทธิ์การเข้าถึงข้อมูลองค์กร
        - ถ้าข้อมูลเป็น Internal แต่คนขอเป็น Public -> ปฏิเสธ
        """
        levels = {
            DataClassification.PUBLIC: 1,
            DataClassification.INTERNAL: 2,
            DataClassification.CONFIDENTIAL: 3,
            DataClassification.RESTRICTED: 4
        }
        
        return levels[requester_level] >= levels[org.classification]

    def process_mixed_data(self, raw_data: list) -> list:
        """
        แยกแยะและจัดการข้อมูลผสม (Mixed Data Batch Processing)
        """
        sanitized_results = []
        for item in raw_data:
            # ตรรกะแยกประเภทข้อมูลอัตโนมัติ (Simple Heuristic)
            if 'email' in item or 'full_name' in item:
                # Treat as Personal Data
                try:
                    p = PersonalInfo(**item)
                    sanitized_results.append(self.sanitize_personal_data(p))
                except Exception as e:
                    sanitized_results.append({"error": "Invalid Personal Data", "raw": str(e)})
            elif 'org_name' in item:
                # Treat as Org Data
                try:
                    o = OrganizationInfo(**item)
                    sanitized_results.append(o.model_dump())
                except Exception:
                    pass
            else:
                # Unknown data type
                sanitized_results.append(item)
                
        return sanitized_results
