from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from pydantic import BaseModel
from ..core.database import get_db
from ..core.dependencies import get_current_active_user, require_role
from ..models.user import User, UserRole
from ..models.event import Event, EventType
from ..services.scheduler import optimize_schedule, suggest_schedule

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


class OptimizeRequest(BaseModel):
    event_ids: List[int]
    constraints: Dict[str, Any] = {}


class SuggestRequest(BaseModel):
    start_date: date
    end_date: date
    event_type: EventType
    constraints: Dict[str, Any] = {}


@router.post("/optimize")
def optimize(
    request: OptimizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SCHEDULER]))
):
    """
    Optimize pilot assignments for given events
    """
    events = db.query(Event).filter(Event.id.in_(request.event_ids)).all()
    if len(events) != len(request.event_ids):
        raise HTTPException(status_code=404, detail="Some events not found")
    
    assignments = optimize_schedule(db, events, request.constraints)
    return {"assignments": assignments}


@router.post("/suggest")
def suggest(
    request: SuggestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SCHEDULER]))
):
    """
    Suggest an optimized schedule for a date range
    """
    suggested_events = suggest_schedule(
        db,
        request.start_date,
        request.end_date,
        request.event_type,
        request.constraints
    )
    return {"suggested_events": suggested_events}
