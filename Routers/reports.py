from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func

import oauth2, schemas, models
from database import get_db
from backend_utils import reset_camera_counting, generate_pdf
import pandas as pd
import datetime, base64, logging
import dateparser

router = APIRouter(prefix="/reports", tags=['reports'])
blogger = logging.getLogger('backend_logger')


# @router.post('/get_dropdown')
# def get_camera_name_number(event_query:schemas.SummaryIds, db: Session = Depends(get_db), 
#                            current_user: int = Depends(oauth2.get_current_user)):

#     try:
#         event_query.start_date_time = dateparser.parse(event_query.start_date_time)
#     except:
#         event_query.start_date_time = datetime.datetime.today().date()
#     try:
#         event_query.end_date_time = dateparser.parse(event_query.end_date_time)
#     except:
#         event_query.end_date_time = datetime.datetime.today().date()

#     summary_query = db.query( models.Counting_Summary.camera_name, models.Counting_Summary.camera_number ).\
#                             filter( models.Counting_Summary.start_time >= event_query.start_date_time,
#                                    models.Counting_Summary.start_time <= event_query.end_date_time )

#     if event_query.camera_number:
#         summary_query = summary_query.filter_by(camera_number = event_query.camera_number)

#     summary_data = summary_query.distinct().all()

#     return summary_data

# @router.post('/get_summary_ids')
# def get_counting_summary_ids(event_query:schemas.SummaryIds, db: Session = Depends(get_db), 
#                              current_user: int = Depends(oauth2.get_current_user)):

#     try:
#         event_query.start_date_time = dateparser.parse(event_query.start_date_time)
#         event_query.end_date_time = dateparser.parse(event_query.end_date_time)
#     except:
#         event_query.start_date_time = datetime.datetime.today().date()
#         event_query.end_date_time = datetime.datetime.today().date()

#     summary_query = db.query( models.Counting_Summary.id, models.Counting_Summary.camera_number ).\
#                             filter( models.Counting_Summary.start_time >= event_query.start_date_time,
#                                    models.Counting_Summary.start_time <= event_query.end_date_time ).\
#                             order_by( models.Counting_Summary.start_time.desc() )

#     if event_query.camera_number is not None:
#         summary_query = summary_query.filter_by(camera_number = event_query.camera_number)
    
#     summary_data = summary_query.distinct().all()
    
#     return summary_data

# @router.post('/get_summary_data')
# def get_summary_data(event_query:schemas.SummaryData, db: Session = Depends(get_db), 
#                      current_user: int = Depends(oauth2.get_current_user)):

#     try:
#         event_query.start_date_time = dateparser.parse(event_query.start_date_time)
#         event_query.end_date_time = dateparser.parse(event_query.end_date_time)
#     except:
#         event_query.start_date_time = datetime.datetime.today().date()
#         event_query.end_date_time = datetime.datetime.today().date()

#     summary_query = db.query( models.Counting_Summary).\
#                             filter( models.Counting_Summary.start_time >= event_query.start_date_time,
#                                    models.Counting_Summary.start_time <= event_query.end_date_time ).\
#                             order_by( models.Counting_Summary.start_time.desc() )
    
#     if event_query.camera_number is not None:
#         summary_query = summary_query.filter_by(camera_number = event_query.camera_number)
    
#     total_events = summary_query.count()
#     offset = (event_query.page_number - 1) * event_query.page_size
#     limit = event_query.page_size

#     summary_data = summary_query.offset(offset).limit(limit).all()
#     response_summary_data = [a.__dict__ for a in summary_data]
    
#     return {'data':response_summary_data, 'page_number': event_query.page_number, 
#             'page_size': event_query.page_size, 'total_records': total_events
#             }

# @router.post('/get_counting_data')
# def get_counting_data(event_query:schemas.CountingData, db: Session = Depends(get_db), 
#                       current_user: int = Depends(oauth2.get_current_user)):
    
#     counting_query = db.query( models.Counting ).order_by( models.Counting.start_time.desc() )
    
#     if event_query.summary_id:
#         counting_query = counting_query.filter_by(summary_id = event_query.summary_id)
    
#     total_events = counting_query.count()
#     offset = (event_query.page_number - 1) * event_query.page_size
#     limit = event_query.page_size
    
#     counting_data = counting_query.offset(offset).limit(limit).all()
    
#     response_counting_data = [a.__dict__ for a in counting_data]

#     return {'data':response_counting_data, 'page_number': event_query.page_number, 
#             'page_size': event_query.page_size, 'total_records': total_events
#             }