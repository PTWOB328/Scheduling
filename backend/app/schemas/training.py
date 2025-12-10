from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from ..models.training import QualificationStatus


class TrainingRequirementCreate(BaseModel):
    requirement_name: str
    requirement_type: str
    event_type: str
    required_count: int = 1
    rules: Dict[str, Any] = {}
    is_active: bool = True


class TrainingRequirementResponse(BaseModel):
    id: int
    requirement_name: str
    requirement_type: str
    event_type: str
    required_count: int
    rules: Dict[str, Any]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PilotStatusResponse(BaseModel):
    id: int
    pilot_id: int
    qualification_status: QualificationStatus
    evaluation_month: date
    requirements_met: Dict[str, Any]
    deficiencies: List[str]
    last_updated: datetime

    class Config:
        from_attributes = True
