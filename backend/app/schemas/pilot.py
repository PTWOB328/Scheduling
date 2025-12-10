from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date


class PilotCreate(BaseModel):
    user_id: Optional[int] = None
    call_sign: Optional[str] = None
    rank: Optional[str] = None
    qualifications: List[str] = []
    availability: Dict[str, Any] = {}
    time_off: List[Dict[str, str]] = []
    b2_requirement: int = 0
    t38_requirement: int = 0
    wst_requirement: int = 0
    notes: Optional[str] = None


class PilotUpdate(BaseModel):
    call_sign: Optional[str] = None
    rank: Optional[str] = None
    qualifications: Optional[List[str]] = None
    availability: Optional[Dict[str, Any]] = None
    time_off: Optional[List[Dict[str, str]]] = None
    b2_requirement: Optional[int] = None
    t38_requirement: Optional[int] = None
    wst_requirement: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class PilotResponse(BaseModel):
    id: int
    user_id: Optional[int]
    call_sign: Optional[str]
    rank: Optional[str]
    qualifications: List[str]
    availability: Dict[str, Any]
    time_off: List[Dict[str, str]]
    b2_requirement: int
    t38_requirement: int
    wst_requirement: int
    notes: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True
