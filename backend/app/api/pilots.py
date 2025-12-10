from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.dependencies import get_current_active_user, require_role
from ..models.user import User, UserRole
from ..models.pilot import Pilot
from ..schemas.pilot import PilotCreate, PilotUpdate, PilotResponse

router = APIRouter(prefix="/api/pilots", tags=["pilots"])


@router.get("/", response_model=List[PilotResponse])
def get_pilots(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    pilots = db.query(Pilot).filter(Pilot.is_active == True).offset(skip).limit(limit).all()
    return pilots


@router.get("/{pilot_id}", response_model=PilotResponse)
def get_pilot(
    pilot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    pilot = db.query(Pilot).filter(Pilot.id == pilot_id).first()
    if not pilot:
        raise HTTPException(status_code=404, detail="Pilot not found")
    return pilot


@router.post("/", response_model=PilotResponse, status_code=status.HTTP_201_CREATED)
def create_pilot(
    pilot_data: PilotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SCHEDULER]))
):
    if pilot_data.call_sign and db.query(Pilot).filter(Pilot.call_sign == pilot_data.call_sign).first():
        raise HTTPException(status_code=400, detail="Call sign already exists")
    
    db_pilot = Pilot(**pilot_data.dict())
    db.add(db_pilot)
    db.commit()
    db.refresh(db_pilot)
    return db_pilot


@router.put("/{pilot_id}", response_model=PilotResponse)
def update_pilot(
    pilot_id: int,
    pilot_data: PilotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SCHEDULER]))
):
    pilot = db.query(Pilot).filter(Pilot.id == pilot_id).first()
    if not pilot:
        raise HTTPException(status_code=404, detail="Pilot not found")
    
    update_data = pilot_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pilot, field, value)
    
    db.commit()
    db.refresh(pilot)
    return pilot


@router.delete("/{pilot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pilot(
    pilot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    pilot = db.query(Pilot).filter(Pilot.id == pilot_id).first()
    if not pilot:
        raise HTTPException(status_code=404, detail="Pilot not found")
    
    pilot.is_active = False
    db.commit()
    return None
