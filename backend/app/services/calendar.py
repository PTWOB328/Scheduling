from icalendar import Calendar, Event as ICalEvent
from typing import List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.event import Event, EventAssignment
from ..models.pilot import Pilot


def generate_ics_for_pilot(
    db: Session,
    pilot_id: int,
    start_date: datetime = None,
    end_date: datetime = None
) -> str:
    """
    Generate ICS calendar file for a specific pilot
    """
    # Get pilot
    pilot = db.query(Pilot).filter(Pilot.id == pilot_id).first()
    if not pilot:
        raise ValueError(f"Pilot {pilot_id} not found")
    
    # Get events for this pilot
    query = (
        db.query(Event)
        .join(EventAssignment)
        .filter(EventAssignment.pilot_id == pilot_id)
    )
    
    if start_date:
        query = query.filter(Event.start_time >= start_date)
    if end_date:
        query = query.filter(Event.start_time <= end_date)
    
    events = query.order_by(Event.start_time).all()
    
    # Create calendar
    cal = Calendar()
    cal.add('prodid', '-//Squadron Scheduler//Squadron Scheduler//EN')
    cal.add('version', '2.0')
    cal.add('X-WR-CALNAME', f'Schedule - {pilot.call_sign or f"Pilot {pilot_id}"}')
    cal.add('X-WR-TIMEZONE', 'UTC')
    
    # Add events
    for event in events:
        ical_event = ICalEvent()
        ical_event.add('summary', event.title)
        ical_event.add('dtstart', event.start_time)
        ical_event.add('dtend', event.end_time)
        ical_event.add('description', f"Event Type: {event.event_type.value}\n{event.notes or ''}")
        ical_event.add('location', f"{event.aircraft.tail_number if event.aircraft else ''}{event.simulator.simulator_id if event.simulator else ''}")
        ical_event.add('uid', f"event-{event.id}@squadron-scheduler")
        ical_event.add('dtstamp', datetime.utcnow())
        
        cal.add_component(ical_event)
    
    return cal.to_ical().decode('utf-8')


def generate_ics_for_all_pilots(
    db: Session,
    start_date: datetime = None,
    end_date: datetime = None
) -> Dict[int, str]:
    """
    Generate ICS files for all pilots
    Returns dictionary mapping pilot_id to ICS content
    """
    pilots = db.query(Pilot).filter(Pilot.is_active == True).all()
    ics_files = {}
    
    for pilot in pilots:
        try:
            ics_content = generate_ics_for_pilot(db, pilot.id, start_date, end_date)
            ics_files[pilot.id] = ics_content
        except Exception as e:
            print(f"Error generating ICS for pilot {pilot.id}: {e}")
            continue
    
    return ics_files
