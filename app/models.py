from pydantic import BaseModel, Field, EmailStr, field_validator
from enum import Enum
from typing import Optional, List
import re

class DataClassification(str, Enum):
    PUBLIC = "public"           # เปิดเผยได้
    INTERNAL = "internal"       # ใช้ภายในบริษัท
    CONFIDENTIAL = "confidential" # ข้อมูลส่วนบุคคล (PII) / ความลับการค้า
    RESTRICTED = "restricted"   # ห้ามเปิดเผยเด็ดขาด (Password, Keys)

class OrganizationInfo(BaseModel):
    org_name: str
    tax_id: Optional[str] = None
    department: str
    classification: DataClassification = Field(default=DataClassification.INTERNAL)

class PersonalInfo(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: str
    national_id: Optional[str] = None
    classification: DataClassification = Field(default=DataClassification.CONFIDENTIAL)

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Basic Thai Phone validation logic
        clean_number = re.sub(r'\D', '', v)
        if len(clean_number) < 9:
            raise ValueError('Invalid phone number format')
        return clean_number
