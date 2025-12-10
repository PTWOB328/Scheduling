from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from ..core.database import get_db
from ..core.dependencies import get_current_active_user, require_role
from ..models.user import User, UserRole
from ..models.training import TrainingRequirement, PilotStatus
from ..schemas.training import TrainingRequirementCreate, TrainingRequirementResponse, PilotStatusResponse
from ..services.cmr_bmc import evaluate_pilot_status, evaluate_all_pilots

router = APIRouter(prefix="/api/training", tags=["training"])


@router.get("/requirements", response_model=List[TrainingRequirementResponse])
def get_requirements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    requirements = db.query(TrainingRequirement).filter(
        TrainingRequirement.is_active == True
    ).all()
    return requirements


@router.post("/requirements", response_model=TrainingRequirementResponse, status_code=status.HTTP_201_CREATED)
def create_requirement(
    requirement_data: TrainingRequirementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SCHEDULER]))
):
    if db.query(TrainingRequirement).filter(
        TrainingRequirement.requirement_name == requirement_data.requirement_name
    ).first():
        raise HTTPException(status_code=400, detail="Requirement name already exists")
    
    db_requirement = TrainingRequirement(**requirement_data.dict())
    db.add(db_requirement)
    db.commit()
    db.refresh(db_requirement)
    return db_requirement


@router.get("/status/pilot/{pilot_id}", response_model=PilotStatusResponse)
def get_pilot_status(
    pilot_id: int,
    evaluation_month: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    status_obj = db.query(PilotStatus).filter(
        PilotStatus.pilot_id == pilot_id,
        PilotStatus.evaluation_month == evaluation_month.replace(day=1)
    ).first()
    
    if not status_obj:
        # Evaluate if not exists
        status_obj = evaluate_pilot_status(db, pilot_id, evaluation_month)
    
    return status_obj


@router.post("/status/evaluate/{pilot_id}", response_model=PilotStatusResponse)
def evaluate_pilot(
    pilot_id: int,
    evaluation_month: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SCHEDULER]))
):
    status_obj = evaluate_pilot_status(db, pilot_id, evaluation_month)
    return status_obj


@router.post("/status/evaluate-all")
def evaluate_all(
    evaluation_month: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SCHEDULER]))
):
    statuses = evaluate_all_pilots(db, evaluation_month)
    return {"evaluated": len(statuses), "statuses": statuses}
