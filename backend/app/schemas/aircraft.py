from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class AircraftCreate(BaseModel):
    tail_number: str
    aircraft_type: str
    availability: Dict[str, Any] = {}
    maintenance_schedule: List[Dict[str, Any]] = []


class AircraftResponse(BaseModel):
    id: int
    tail_number: str
    aircraft_type: str
    availability: Dict[str, Any]
    maintenance_schedule: List[Dict[str, Any]]
    is_active: bool

    class Config:
        from_attributes = True
