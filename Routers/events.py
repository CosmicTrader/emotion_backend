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
