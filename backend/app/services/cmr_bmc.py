from typing import Dict, List, Any
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from ..models.training import TrainingRequirement, PilotStatus, QualificationStatus
from ..models.pilot import Pilot
from ..models.event import Event, EventAssignment, EventType, EventStatus


def evaluate_pilot_status(
    db: Session,
    pilot_id: int,
    evaluation_month: date
) -> PilotStatus:
    """
    Evaluate a pilot's CMR/BMC status for a given month
    """
    pilot = db.query(Pilot).filter(Pilot.id == pilot_id).first()
    if not pilot:
        raise ValueError(f"Pilot {pilot_id} not found")
    
    # Get all active training requirements
    requirements = db.query(TrainingRequirement).filter(
        TrainingRequirement.is_active == True
    ).all()
    
    # Calculate month start and end
    month_start = date(evaluation_month.year, evaluation_month.month, 1)
    if evaluation_month.month == 12:
        month_end = date(evaluation_month.year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(evaluation_month.year, evaluation_month.month + 1, 1) - timedelta(days=1)
    
    # Get events for this pilot in the evaluation month
    events = db.query(Event).join(EventAssignment).filter(
        EventAssignment.pilot_id == pilot_id,
        Event.start_time >= datetime.combine(month_start, datetime.min.time()),
        Event.start_time <= datetime.combine(month_end, datetime.max.time()),
        Event.status == EventStatus.EFFECTIVE
    ).all()
    
    # Count events by type
    flight_count = sum(1 for e in events if e.event_type == EventType.FLIGHT)
    sim_count = sum(1 for e in events if e.event_type == EventType.SIMULATOR)
    
    # Evaluate each requirement
    requirements_met = {}
    deficiencies = []
    
    for requirement in requirements:
        met = False
        
        if requirement.requirement_type == "monthly":
            # Check if requirement is met this month
            if requirement.event_type == "flight":
                met = flight_count >= requirement.required_count
            elif requirement.event_type == "simulator":
                met = sim_count >= requirement.required_count
            elif requirement.event_type == "both":
                met = (flight_count + sim_count) >= requirement.required_count
        elif requirement.requirement_type == "quarterly":
            # Check last 3 months
            quarter_start = month_start - timedelta(days=90)
            quarter_events = db.query(Event).join(EventAssignment).filter(
                EventAssignment.pilot_id == pilot_id,
                Event.start_time >= datetime.combine(quarter_start, datetime.min.time()),
                Event.start_time <= datetime.combine(month_end, datetime.max.time()),
                Event.status == EventStatus.EFFECTIVE
            ).all()
            
            quarter_flight_count = sum(1 for e in quarter_events if e.event_type == EventType.FLIGHT)
            quarter_sim_count = sum(1 for e in quarter_events if e.event_type == EventType.SIMULATOR)
            
            if requirement.event_type == "flight":
                met = quarter_flight_count >= requirement.required_count
            elif requirement.event_type == "simulator":
                met = quarter_sim_count >= requirement.required_count
            elif requirement.event_type == "both":
                met = (quarter_flight_count + quarter_sim_count) >= requirement.required_count
        
        requirements_met[requirement.requirement_name] = met
        
        if not met:
            deficiencies.append(requirement.requirement_name)
    
    # Determine qualification status
    # CMR requires all requirements met
    # BMC requires core requirements met (can be configured)
    qualification_status = QualificationStatus.NOT_QUALIFIED
    
    if all(requirements_met.values()):
        qualification_status = QualificationStatus.CMR
    elif len(deficiencies) <= 1:  # Allow one deficiency for BMC (configurable)
        qualification_status = QualificationStatus.BMC
    
    # Get or create pilot status
    pilot_status = db.query(PilotStatus).filter(
        PilotStatus.pilot_id == pilot_id,
        PilotStatus.evaluation_month == month_start
    ).first()
    
    if not pilot_status:
        pilot_status = PilotStatus(
            pilot_id=pilot_id,
            qualification_status=qualification_status,
            evaluation_month=month_start,
            requirements_met=requirements_met,
            deficiencies=deficiencies
        )
        db.add(pilot_status)
    else:
        pilot_status.qualification_status = qualification_status
        pilot_status.requirements_met = requirements_met
        pilot_status.deficiencies = deficiencies
        pilot_status.last_updated = datetime.utcnow()
    
    db.commit()
    db.refresh(pilot_status)
    return pilot_status


def evaluate_all_pilots(db: Session, evaluation_month: date) -> List[PilotStatus]:
    """Evaluate status for all active pilots"""
    pilots = db.query(Pilot).filter(Pilot.is_active == True).all()
    statuses = []
    
    for pilot in pilots:
        try:
            status = evaluate_pilot_status(db, pilot.id, evaluation_month)
            statuses.append(status)
        except Exception as e:
            print(f"Error evaluating pilot {pilot.id}: {e}")
            continue
    
    return statuses
