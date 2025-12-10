from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models.event import EventType, EventStatus


class EventAssignmentCreate(BaseModel):
    pilot_id: int
    position: str


class EventAssignmentResponse(BaseModel):
    id: int
    pilot_id: int
    position: str
    
    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    event_type: EventType
    title: str
    start_time: datetime
    end_time: datetime
    aircraft_id: Optional[int] = None
    simulator_id: Optional[int] = None
    crew_composition: Dict[str, Any] = {}
    notes: Optional[str] = None
    assignments: List[EventAssignmentCreate] = []


class EventUpdate(BaseModel):
    title: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[EventStatus] = None
    aircraft_id: Optional[int] = None
    simulator_id: Optional[int] = None
    crew_composition: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class EventResponse(BaseModel):
    id: int
    event_type: EventType
    title: str
    start_time: datetime
    end_time: datetime
    status: EventStatus
    aircraft_id: Optional[int]
    simulator_id: Optional[int]
    crew_composition: Dict[str, Any]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    assignments: List[EventAssignmentResponse] = []

    class Config:
        from_attributes = True
