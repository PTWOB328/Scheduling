from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from ..core.database import get_db
from ..core.dependencies import get_current_active_user, require_role
from ..models.user import User, UserRole
from ..models.event import Event, EventAssignment, EventStatus
from ..schemas.event import EventCreate, EventUpdate, EventResponse, EventAssignmentCreate, EventAssignmentResponse

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/", response_model=List[EventResponse])
def get_events(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    event_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Event)
    
    if start_date:
        query = query.filter(Event.start_time >= start_date)
    if end_date:
        query = query.filter(Event.start_time <= end_date)
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    events = query.options(joinedload(Event.assignments)).order_by(Event.start_time).offset(skip).limit(limit).all()
    return events


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    event = db.query(Event).options(joinedload(Event.assignments)).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SCHEDULER]))
):
    db_event = Event(**event_data.dict(exclude={"assignments"}))
    db.add(db_event)
    db.flush()
    
    # Create assignments
    for assignment_data in event_data.assignments:
        assignment = EventAssignment(
            event_id=db_event.id,
            pilot_id=assignment_data.pilot_id,
            position=assignment_data.position
        )
        db.add(assignment)
    
    db.commit()
    db.refresh(db_event)
    return db_event


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SCHEDULER]))
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    update_data = event_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    event.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SCHEDULER]))
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    return None


@router.post("/{event_id}/assignments", status_code=status.HTTP_201_CREATED)
def add_assignment(
    event_id: int,
    assignment_data: EventAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SCHEDULER]))
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    assignment = EventAssignment(
        event_id=event_id,
        pilot_id=assignment_data.pilot_id,
        position=assignment_data.position
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.patch("/{event_id}/status", response_model=EventResponse)
def update_event_status(
    event_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SCHEDULER]))
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    try:
        event.status = EventStatus(new_status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {new_status}")
    
    event.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(event)
    return event
