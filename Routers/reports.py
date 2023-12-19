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


@router.post('/attendence_summary')
def attendence_summary(params:schemas.SummaryQuery, db: Session = Depends(get_db), 
                             current_user: int = Depends(oauth2.get_current_user)):

    try:
        params.start_date = dateparser.parse(params.start_date)
        params.end_date = dateparser.parse(params.end_date)
    except:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"Date Values are not valid."))

    summary_data = (
        db.query(models.Attendence_Summary)
        .filter(models.Attendence_Summary.date >= params.start_date,
                models.Attendence_Summary.date <=  params.end_date,
                models.Attendence_Summary.course_id.in_(params.course_id),
                models.Attendence_Summary.room_number.in_(params.room_number),
                )
        .order_by(models.Attendence_Summary.date.asc() 
                  )
        .all()
        )

    return summary_data


@router.post('/emotion_summary')
def emotion_summary(params:schemas.SummaryQuery, db: Session = Depends(get_db), 
                             current_user: int = Depends(oauth2.get_current_user)):

    try:
        params.start_date = dateparser.parse(params.start_date)
        params.end_date = dateparser.parse(params.end_date)
    except:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"Date Values are not valid."))

    summary_data = (
        db.query(models.Emotion_Summary)
        .filter(models.Attendence_Summary.date >= params.start_date,
                models.Attendence_Summary.date <=  params.end_date,
                models.Emotion_Summary.course_id.in_(params.course_id),
                models.Emotion_Summary.room_number.in_(params.room_number),
                )
        .order_by(models.Attendence_Summary.date.asc() 
                  )
        .all()
        )

    return summary_data


@router.post('/emotion_data')
def emotion_data(params:schemas.SummaryId, db: Session = Depends(get_db), 
                             current_user: int = Depends(oauth2.get_current_user)):

    summary_data = (
        db.query(models.Emotion)
        .filter(models.Emotion.id == params.summary_id)
        .order_by(models.Emotion.timestamp)
        .all()
        )

    return summary_data

@router.post('/attendence_data')
def attendance_data(params:schemas.SummaryId, db: Session = Depends(get_db), 
                             current_user: int = Depends(oauth2.get_current_user)):

    summary_data = (
        db.query(models.Attendance)
        .filter(models.Attendance.id == params.summary_id)
        .order_by(models.Attendance.timestamp)
        .all()
        )

    return summary_data
