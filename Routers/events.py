from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func

import oauth2, schemas, models
from database import get_db
from backend_utils import reset_camera_counting, generate_pdf
import pandas as pd
import datetime, base64, logging
import dateparser

router = APIRouter(prefix="/events", tags=['events'])
blogger = logging.getLogger('backend_logger')
@router.post('/get_events')
def get_events(event_query: schemas.EventPage, db: Session = Depends(get_db), 
               current_user: int = Depends(oauth2.get_current_user)):

    try:
        event_query.date = dateparser.parse(event_query.date)
    except:
        event_query.date = datetime.datetime.today().date()

    query = db.query(models.Events.id, models.Events.date, models.Events.time, 
                     models.Events.camera_name, models.Events.note,models.Events.event, 
                     models.Events.thumbnail, models.Events.tele_created, 
                     models.Events.vehicle_number, models.Events.vehicle_category).\
                    filter(models.Events.date==event_query.date)

    if event_query.event != 'all':
        query = query.filter_by(event=event_query.event)

    total_events = query.count()
    offset = (event_query.page_number - 1) * event_query.page_size
    limit = event_query.page_size

    events = query.offset(offset).limit(limit).all()

    event_list = []
    for event in events:

        _event = {
                'id' : event.id,
               'date' : event.date,
               'time' : event.time,
               'camera_name' : event.camera_name,
               'event' : (event.event),
               'thumbnail' : base64.b64encode(event.thumbnail).decode('utf-8') if event.thumbnail is not None else None,
               'alert_created' : event.tele_created,
               'vehicle_number': event.vehicle_number if event.vehicle_number else None,
               'vehicle_category' : event.vehicle_category if event.vehicle_category else None
               }

        event_list.append(_event)

    return {'data':event_list, 'page_number': event_query.page_number, 
            'page_size': event_query.page_size, 'total_records': total_events
            }

@router.post('/get_event_image')
def get_event_image(id:int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    image = db.query(models.Images.image).filter_by(event_id = id).first()
    if image:
        return base64.b64encode(image.image).decode('utf-8')
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=(
            f"Requested Image not found"))


@router.post('/download_csv')
def download_alerts_csv(event_query: schemas.EventCount, db: Session = Depends(get_db), 
                        current_user: int = Depends(oauth2.get_current_user)):

    try:
        event_query.date = dateparser.parse(event_query.date)
    except:
        event_query.date = datetime.datetime.today().date()

    try:
        event_query.end_date = dateparser.parse(event_query.end_date)
    except:
        event_query.end_date = event_query.date

    db_query = db.query(models.Events.date, models.Events.time, models.Events.event, 
                        models.Events.camera_name, models.Events.vehicle_number, 
                        models.Events.vehicle_category).filter(models.Events.date >= event_query.date, 
                                                               models.Events.date <= event_query.end_date)

    if event_query.event != 'all':
        db_query = db_query.filter(models.Events.event == event_query.event)

    event_list = db_query.all()

    data = pd.DataFrame(event_list, 
                        columns=['date', 'time', 'event', 'camera_name', 'vehicle_number', 'vehicle_category']
                        )
    csv_file = data.to_csv(index=False)

    return Response(content = csv_file, media_type="text/csv", 
                    headers = { 'Content-Disposition': f'attachment; filename="{str(event_query.date.date()) }.csv"' } 
                    )

@router.post('/download_pdf')
def download_alerts_pdf(event_query: schemas.EventCount, db: Session = Depends(get_db), 
                        current_user: int = Depends(oauth2.get_current_user)):
    print(event_query.__dict__)
    try:
        event_query.date = dateparser.parse(event_query.date)
    except:
        event_query.date = datetime.datetime.today().date()

    try:
        event_query.end_date = dateparser.parse(event_query.end_date)
    except:
        event_query.end_date = event_query.date
    
    events_alias = aliased(models.Events)
    images_alias = aliased(models.Images)

    db_query = db.query(events_alias.id, events_alias.timestamp, events_alias.camera_name,
                        events_alias.location, events_alias.vehicle_category, events_alias.event, 
                        events_alias.note, events_alias.vehicle_number, images_alias.image)

    db_query = db_query.outerjoin( images_alias, images_alias.event_id == events_alias.id )

    db_query = db_query.filter(events_alias.date >= event_query.date, events_alias.date <= event_query.end_date)
    
    if event_query.event != 'all':
        db_query = db_query.filter(events_alias.event == event_query.event)

    event_list = db_query.all()

    headers = {'Sr No':40, 'Date Time':70, 'Cam Name':70, 'Location':60, 
               'Vehicle':45, 'Alert':50, 'Speed':40, 'Num Plate':80, 'Image':110}

    pdf_file = generate_pdf(event_list, headers)

    return Response(content=pdf_file.getvalue(), media_type="application/pdf",  
                    headers={'Content-Disposition': f'attachment; filename="{str(event_query.date.date())}.pdf"'}
                    )

@router.post('/get_events_count')
def get_events_count(event_query: schemas.EventCount, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    try:
        event_query.date = dateparser.parse(event_query.date)
    except:
        event_query.date = datetime.datetime.today().date()

    try:
        event_query.end_date = dateparser.parse(event_query.end_date)
    except:
        event_query.end_date = event_query.date

    query = db.query(models.Events.event, func.count(models.Events.event)).\
                filter(models.Events.date >= event_query.date, models.Events.date <= event_query.end_date)

    results = query.group_by(models.Events.event).all()

    results_dict = {event: count for event, count in results}
    
    return results_dict


@router.post('/reset_camera_counting', status_code=status.HTTP_200_OK)
def reset_counting(camera_number:schemas.CameraNumber, db: Session = Depends(get_db), 
                   current_user: int = Depends(oauth2.get_current_user)):
    
    reset_camera_counting(camera_number= camera_number.camera_number, db= db)
    return

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