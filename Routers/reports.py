from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, between, or_, and_

import oauth2, schemas, models
from database import get_db
import pandas as pd
import datetime, base64, logging
import dateparser

router = APIRouter(prefix="/reports", tags=['reports'])
blogger = logging.getLogger('backend_logger')

@router.get('/filter_data')
def filter_data(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    course_name = [a for (a,) in db.query(models.Session.course_name).distinct().all()]
    room_number = [a for (a,) in db.query(models.Session.room_number).distinct().all()]
    session_id = [a for (a,) in db.query(models.Session.session_id).distinct().all()] 
   
    return {'course_name': course_name, 'room_number': room_number, 'session_id': session_id}

@router.post('/summary')
def summary(params:schemas.SummaryQuery, db: Session = Depends(get_db), 
                             current_user: int = Depends(oauth2.get_current_user)):

    try:
        params.start_date = dateparser.parse(params.start_date)
        params.end_date = dateparser.parse(params.end_date)
    except:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"Date Values are not valid."))

    try:
        params.start_time = datetime.datetime.strptime(params.start_time, '%H:%M')
        params.end_time = datetime.datetime.strptime(params.end_time, '%H:%M')
    except:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"Time Values are not valid."))
    queries = []

    if 'all' not in params.course_name:
        queries.append(and_(models.Summary.course_name.in_(params.course_name)))

    if 0 not in params.room_number:
        queries.append(and_(models.Summary.room_number.in_(params.room_number)))
    
    if 0 not in params.session_id:
        queries.append(and_(models.Summary.session_id.in_(params.session_id)))
    
    summary_data = (
        db.query(models.Summary)
        .filter(models.Summary.date >= params.start_date,
                models.Summary.date <=  params.end_date,
                models.Summary.start_time >= params.start_time,
                models.Summary.end_time <= params.end_time,
                *queries
                # models.Summary.course_name.in_(params.course_name),
                # models.Summary.room_number.in_(params.room_number),
                # models.Summary.session_id.in_(params.session_id),
                )
        .order_by(models.Summary.date.desc() 
                  )
        .all()
        )
    return summary_data

@router.post('/summary_data')
def summary_data(params:schemas.SummaryId, db: Session = Depends(get_db), 
                             current_user: int = Depends(oauth2.get_current_user)):

    emotion_data = (
        db.query(models.Emotion)
        .filter(models.Emotion.summary_id == params.summary_id)
        .order_by(models.Emotion.student_id)
        .all()
        )

    return emotion_data

@router.post('/get_home_page_summary')
def get_home_page_summary(query_params: schemas.HomeSummary, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    try:
        query_params.date = dateparser.parse(query_params.date)
    except:
        query_params.date = datetime.datetime.today().date()

    data = (db.query(models.Summary)
            .filter(models.Summary.date == query_params.date, models.Summary.completed == True)
            )
    response = []
    for summary in data:
        response.append({
            'room_number':summary.room_number,
            'course_name':summary.course_name,
            'start_time':summary.start_time,
            'end_time':summary.end_time,
            'summary_id':summary.id,
            'present':summary.present,
            'absent':summary.absent,
            'total':summary.total,
            'ratio':summary.ratio,
            'anger':summary.anger,
            'disgust':summary.disgust,
            'fear':summary.fear,
            'happy':summary.happy,
            'neutral':summary.neutral,
            'sad':summary.sad,
            'surprise':summary.surprise,
            'unknown':summary.unknown
        })        
    return response

@router.get('/get_live_class_summary', status_code=status.HTTP_200_OK)
def get_live_class_summary(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    live_sessions = (db.query(models.Summary.room_number, models.Summary.course_name, models.Summary.present, models.Summary.absent)
                    .filter(models.Summary.completed != True)
                    .all()
                    )
    data = [{
			'room_number': 1,
			'course_name': "Maths",
			'present': 74,
			'absent': 4,
		},
		{
			'room_number': 1,
			'course_name': "Science",
			'present': 29,
			'absent': 3,
		},
		{
			'room_number': 1,
			'course_name': "Physics",
			'present': 35,
			'absent': 1,
		},
		{
			'room_number': 1,
			'course_name': "Chemistry",
			'present': 25,
			'absent': 5,
		},
		{
			'room_number': 1,
			'course_name': "History",
			'present': 20,
			'absent': 2,
		},
		]
    return data



# @router.post('/download_csv')
# def download_alerts_csv(event_query: schemas.EventCount, db: Session = Depends(get_db), 
#                         current_user: int = Depends(oauth2.get_current_user)):

#     try:
#         event_query.date = dateparser.parse(event_query.date)
#     except:
#         event_query.date = datetime.datetime.today().date()

#     try:
#         event_query.end_date = dateparser.parse(event_query.end_date)
#     except:
#         event_query.end_date = event_query.date

#     db_query = db.query(models.Event.date, models.Event.time, models.Event.event, 
#                         models.Event.camera_name, models.Event.vehicle_number, 
#                         models.Event.vehicle_category).filter(models.Event.date >= event_query.date, 
#                                                                models.Event.date <= event_query.end_date)

#     if event_query.event != 'all':
#         db_query = db_query.filter(models.Event.event == event_query.event)

#     event_list = db_query.all()

#     data = pd.DataFrame(event_list, 
#                         columns=['date', 'time', 'event', 'camera_name', 'vehicle_number', 'vehicle_category']
#                         )
#     csv_file = data.to_csv(index=False)

#     return Response(content = csv_file, media_type="text/csv", 
#                     headers = { 'Content-Disposition': f'attachment; filename="{str(event_query.date.date()) }.csv"' }
#                     )
