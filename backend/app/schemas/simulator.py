from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class SimulatorCreate(BaseModel):
    simulator_id: str
    simulator_type: str
    availability: Dict[str, Any] = {}
    maintenance_schedule: List[Dict[str, Any]] = []


class SimulatorResponse(BaseModel):
    id: int
    simulator_id: str
    simulator_type: str
    availability: Dict[str, Any]
    maintenance_schedule: List[Dict[str, Any]]
    is_active: bool

    class Config:
        from_attributes = True
