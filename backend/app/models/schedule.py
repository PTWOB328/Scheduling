from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class ScheduleVersion(Base):
    __tablename__ = "schedule_versions"

    id = Column(Integer, primary_key=True, index=True)
    version_number = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    changes = Column(JSON, default=dict)  # Track what changed
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    creator = relationship("User")
