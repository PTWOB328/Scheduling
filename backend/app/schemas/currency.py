from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import date, datetime


class CurrencyRecordCreate(BaseModel):
    pilot_id: int
    currency_type: str
    last_completed_date: Optional[date] = None
    expiration_date: Optional[date] = None
    status: Optional[str] = None
    raw_data: Dict[str, Any] = {}


class CurrencyRecordResponse(BaseModel):
    id: int
    pilot_id: int
    currency_type: str
    last_completed_date: Optional[date]
    expiration_date: Optional[date]
    status: Optional[str]
    raw_data: Dict[str, Any]
    imported_at: datetime

    class Config:
        from_attributes = True
