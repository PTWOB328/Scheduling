from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from ..models.pilot import Pilot
from ..models.event import Event, EventAssignment, EventType
from ..models.aircraft import Aircraft
from ..models.simulator import Simulator
from ..models.currency import CurrencyRecord


def check_pilot_availability(
    db: Session,
    pilot: Pilot,
    start_time: datetime,
    end_time: datetime
) -> bool:
    """Check if pilot is available for a given time slot"""
    # Check time off
    for time_off_period in pilot.time_off:
        if isinstance(time_off_period, dict):
            off_start = datetime.fromisoformat(time_off_period.get('start', ''))
            off_end = datetime.fromisoformat(time_off_period.get('end', ''))
            if not (end_time < off_start or start_time > off_end):
                return False
    
    # Check existing assignments
    conflicting_events = (
        db.query(Event)
        .join(EventAssignment)
        .filter(
            EventAssignment.pilot_id == pilot.id,
            Event.start_time < end_time,
            Event.end_time > start_time
        )
        .all()
    )
    
    return len(conflicting_events) == 0


def get_pilots_needing_currency(
    db: Session,
    currency_type: str,
    days_until_expiration: int = 30
) -> List[Pilot]:
    """Get pilots who need currency training"""
    cutoff_date = date.today() + timedelta(days=days_until_expiration)
    
    # Get pilots with expired or expiring currency
    currency_records = db.query(CurrencyRecord).filter(
        CurrencyRecord.currency_type == currency_type,
        CurrencyRecord.expiration_date <= cutoff_date
    ).all()
    
    pilot_ids = [cr.pilot_id for cr in currency_records]
    pilots = db.query(Pilot).filter(
        Pilot.id.in_(pilot_ids),
        Pilot.is_active == True
    ).all()
    
    return pilots


def optimize_schedule(
    db: Session,
    events: List[Event],
    constraints: Dict[str, Any]
) -> Dict[int, List[int]]:
    """
    Optimize schedule by assigning pilots to events
    
    Args:
        db: Database session
        events: List of events to schedule
        constraints: Dictionary of constraints (availability, currency, fairness, etc.)
    
    Returns:
        Dictionary mapping event_id to list of pilot_ids
    """
    assignments = {}
    
    # Get all active pilots
    pilots = db.query(Pilot).filter(Pilot.is_active == True).all()
    
    # Sort events by priority (e.g., currency requirements first)
    sorted_events = sorted(events, key=lambda e: e.start_time)
    
    # Track pilot workload for fairness
    pilot_workload = {pilot.id: 0 for pilot in pilots}
    
    for event in sorted_events:
        available_pilots = []
        
        # Find available pilots
        for pilot in pilots:
            if check_pilot_availability(db, pilot, event.start_time, event.end_time):
                # Check qualifications if needed
                if constraints.get('check_qualifications', False):
                    # Add qualification checks here
                    pass
                
                available_pilots.append(pilot)
        
        # Sort by workload (fairness) and currency needs
        if constraints.get('prioritize_currency', False):
            # Prioritize pilots who need currency training
            currency_needing = get_pilots_needing_currency(
                db,
                constraints.get('currency_type', ''),
                constraints.get('currency_days', 30)
            )
            currency_pilot_ids = {p.id for p in currency_needing}
            
            available_pilots.sort(
                key=lambda p: (
                    p.id not in currency_pilot_ids,  # Currency needs first
                    pilot_workload[p.id]  # Then by workload
                )
            )
        else:
            available_pilots.sort(key=lambda p: pilot_workload[p.id])
        
        # Assign pilots based on crew composition requirements
        required_positions = event.crew_composition.get('positions', {})
        assigned_pilots = []
        
        for position, count in required_positions.items():
            for _ in range(count):
                if available_pilots:
                    pilot = available_pilots.pop(0)
                    assigned_pilots.append(pilot.id)
                    pilot_workload[pilot.id] += 1
        
        assignments[event.id] = assigned_pilots
    
    return assignments


def suggest_schedule(
    db: Session,
    start_date: date,
    end_date: date,
    event_type: EventType,
    constraints: Dict[str, Any]
) -> List[Event]:
    """
    Suggest an optimized schedule for a date range
    """
    # This is a simplified version - in production, you'd want more sophisticated
    # constraint satisfaction algorithms
    
    # Get available resources
    if event_type == EventType.FLIGHT:
        resources = db.query(Aircraft).filter(Aircraft.is_active == True).all()
    else:
        resources = db.query(Simulator).filter(Simulator.is_active == True).all()
    
    # Generate suggested events (simplified - would need more logic)
    suggested_events = []
    current_date = start_date
    
    while current_date <= end_date:
        # Add logic to create suggested events based on:
        # - Resource availability
        # - Pilot availability
        # - Currency requirements
        # - Training requirements
        pass
    
    return suggested_events
