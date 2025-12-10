from sqlalchemy import Column, Integer, String, Date, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class CurrencyRecord(Base):
    __tablename__ = "currency_records"

    id = Column(Integer, primary_key=True, index=True)
    pilot_id = Column(Integer, ForeignKey("pilots.id"), nullable=False)
    currency_type = Column(String, nullable=False)  # Type of currency requirement
    last_completed_date = Column(Date, nullable=True)
    expiration_date = Column(Date, nullable=True)
    status = Column(String, nullable=True)  # "current", "expiring", "expired"
    raw_data = Column(JSON, default=dict)  # Store original spreadsheet data
    imported_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pilot = relationship("Pilot", back_populates="currency_records")
