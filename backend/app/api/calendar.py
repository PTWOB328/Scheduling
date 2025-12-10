from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from datetime import datetime
from ..core.database import get_db
from ..core.dependencies import get_current_active_user
from ..models.user import User
from ..models.pilot import Pilot
from ..services.calendar import generate_ics_for_pilot

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


@router.get("/pilot/{pilot_id}/ics")
def get_pilot_calendar(
    pilot_id: int,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get ICS calendar file for a pilot
    Can be accessed by the pilot themselves or schedulers/admins
    """
    # Check permissions
    if current_user.role.value not in ['admin', 'scheduler']:
        # Pilots can only access their own calendar
        pilot = db.query(Pilot).filter(Pilot.user_id == current_user.id).first()
        if not pilot or pilot.id != pilot_id:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own calendar"
            )
    
    ics_content = generate_ics_for_pilot(db, pilot_id, start_date, end_date)
    
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename=pilot_{pilot_id}_schedule.ics"
        }
    )


@router.get("/pilot/{pilot_id}/calendar-url")
def get_pilot_calendar_url(
    pilot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the calendar subscription URL for a pilot
    This URL can be added to calendar applications and will auto-update
    """
    from ..core.config import settings
    import os
    
    # Generate a unique token for the pilot (in production, use a secure token)
    # For now, we'll use a simple approach - in production, generate secure tokens
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    calendar_url = f"{base_url}/api/calendar/pilot/{pilot_id}/ics"
    
    return {
        "calendar_url": calendar_url,
        "instructions": "Add this URL to your calendar application (Google Calendar, Outlook, Apple Calendar) as a calendar subscription"
    }
