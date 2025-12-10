from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy.orm import relationship
from ..core.database import Base


class Aircraft(Base):
    __tablename__ = "aircraft"

    id = Column(Integer, primary_key=True, index=True)
    tail_number = Column(String, unique=True, index=True, nullable=False)
    aircraft_type = Column(String, nullable=False)
    availability = Column(JSON, default=dict)  # Availability schedule
    maintenance_schedule = Column(JSON, default=list)  # Maintenance periods
    is_active = Column(Boolean, default=True)
    
    # Relationships
    events = relationship("Event", back_populates="aircraft")
