from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import date
from ..core.database import Base


class Pilot(Base):
    __tablename__ = "pilots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)
    call_sign = Column(String, unique=True, index=True, nullable=True)
    rank = Column(String, nullable=True)
    qualifications = Column(JSON, default=list)  # List of qualification types
    availability = Column(JSON, default=dict)  # Availability schedule
    time_off = Column(JSON, default=list)  # List of date ranges for time off
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="pilot_profile")
    event_assignments = relationship("EventAssignment", back_populates="pilot")
    currency_records = relationship("CurrencyRecord", back_populates="pilot")
    pilot_statuses = relationship("PilotStatus", back_populates="pilot")
