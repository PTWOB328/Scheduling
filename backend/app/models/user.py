from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from ..core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SCHEDULER = "scheduler"
    PILOT = "pilot"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.PILOT, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationship to pilot profile if user is a pilot
    pilot_profile = relationship("Pilot", back_populates="user", uselist=False)
