from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base


class EventType(str, enum.Enum):
    B2 = "b-2"
    OB2 = "ob2"
    OB3 = "ob3"
    LOCAL = "local"
    MADDOG = "maddog"
    WST = "wst"


class EventStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    EFFECTIVE = "effective"
    CANCELLED = "cancelled"


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(Enum(EventType), nullable=False)
    title = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(EventStatus), default=EventStatus.SCHEDULED)
    aircraft_id = Column(Integer, ForeignKey("aircraft.id"), nullable=True)
    simulator_id = Column(Integer, ForeignKey("simulators.id"), nullable=True)
    crew_composition = Column(JSON, default=dict)  # Required crew positions
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    aircraft = relationship("Aircraft", back_populates="events")
    simulator = relationship("Simulator", back_populates="events")
    assignments = relationship("EventAssignment", back_populates="event", cascade="all, delete-orphan")


class EventAssignment(Base):
    __tablename__ = "event_assignments"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    pilot_id = Column(Integer, ForeignKey("pilots.id"), nullable=False)
    position = Column(String, nullable=False)  # e.g., "pilot", "co-pilot", "instructor"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    event = relationship("Event", back_populates="assignments")
    pilot = relationship("Pilot", back_populates="event_assignments")
