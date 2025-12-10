from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import tempfile
import os
from ..core.database import get_db
from ..core.dependencies import get_current_active_user, require_role
from ..models.user import User, UserRole
from ..models.pilot import Pilot
from ..services.currency import import_currency_records
from ..schemas.currency import CurrencyRecordResponse

router = APIRouter(prefix="/api/currency", tags=["currency"])


@router.post("/import", response_model=List[CurrencyRecordResponse])
def import_currency(
    file: UploadFile = File(...),
    file_type: str = "excel",  # "excel" or "csv"
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SCHEDULER]))
):
    """
    Import currency data from spreadsheet
    Note: This is a simplified version. In production, you'd want to:
    - Accept column mapping configuration
    - Accept pilot mapping configuration
    - Handle file validation better
    """
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as tmp_file:
        content = file.file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # Get all pilots for mapping (simplified - in production, use provided mapping)
        pilots = db.query(Pilot).all()
        pilot_mapping = {}
        for pilot in pilots:
            if pilot.call_sign:
                pilot_mapping[pilot.call_sign] = pilot.id
        
        # Default column mapping (should be configurable)
        column_mapping = {
            'call_sign': 'call_sign',  # Adjust based on your spreadsheet
            'currency_type': 'currency_type',
            'last_completed_date': 'last_completed_date',
            'expiration_date': 'expiration_date'
        }
        
        records = import_currency_records(
            db=db,
            file_path=tmp_file_path,
            file_type=file_type,
            pilot_mapping=pilot_mapping,
            column_mapping=column_mapping
        )
        
        return records
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error importing currency: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)


@router.get("/pilot/{pilot_id}", response_model=List[CurrencyRecordResponse])
def get_pilot_currency(
    pilot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from ..models.currency import CurrencyRecord
    
    records = db.query(CurrencyRecord).filter(CurrencyRecord.pilot_id == pilot_id).all()
    return records
