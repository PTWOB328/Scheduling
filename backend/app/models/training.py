from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Date, DateTime, Enum, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base


class QualificationStatus(str, enum.Enum):
    CMR = "cmr"  # Combat Mission Ready
    BMC = "bmc"  # Basic Mission Qualification
    NOT_QUALIFIED = "not_qualified"


class TrainingRequirement(Base):
    __tablename__ = "training_requirements"

    id = Column(Integer, primary_key=True, index=True)
    requirement_name = Column(String, nullable=False, unique=True)
    requirement_type = Column(String, nullable=False)  # "monthly", "quarterly", "annual"
    event_type = Column(String, nullable=False)  # "flight", "simulator", "both"
    required_count = Column(Integer, default=1)
    rules = Column(JSON, default=dict)  # Flexible rules configuration
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PilotStatus(Base):
    __tablename__ = "pilot_status"
    __table_args__ = (
        UniqueConstraint('pilot_id', 'evaluation_month', name='uq_pilot_evaluation_month'),
    )

    id = Column(Integer, primary_key=True, index=True)
    pilot_id = Column(Integer, ForeignKey("pilots.id"), nullable=False, index=True)
    qualification_status = Column(Enum(QualificationStatus), default=QualificationStatus.NOT_QUALIFIED)
    evaluation_month = Column(Date, nullable=False, index=True)  # Month being evaluated
    requirements_met = Column(JSON, default=dict)  # Track which requirements are met
    deficiencies = Column(JSON, default=list)  # List of deficiencies
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pilot = relationship("Pilot", back_populates="pilot_statuses")
