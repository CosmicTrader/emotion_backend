from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, between, or_

import oauth2, schemas, models
from database import get_db
from backend_utils import reset_camera_counting, generate_pdf
import pandas as pd
import datetime, base64, logging
import dateparser

router = APIRouter(prefix="/reports", tags=['reports'])
blogger = logging.getLogger('backend_logger')


@router.post('/get_attendence_summary')
def get_attendence_summary(params:schemas.Attendence_Summary, db: Session = Depends(get_db), 
                             current_user: int = Depends(oauth2.get_current_user)):

    try:
        params.start_date = dateparser.parse(params.start_date)
        params.end_date = dateparser.parse(params.end_date)
    except:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"Date Values are not valid."))

    summary_data = (
        db.query(models.Attendence_Summary)
        .filter(between(models.Attendence_Summary.timestamp, params.start_date, params.end_date),
                models.Attendence_Summary.course_id.in_(params.course_id),
                models.Attendence_Summary.room_number.in_(params.room_number),
                )
        .order_by(models.Attendence_Summary.timestamp.asc() 
                  )
        .all()
        )

    return summary_data
