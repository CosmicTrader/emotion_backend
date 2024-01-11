from fastapi import APIRouter, Depends, Response, status, HTTPException, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, between, or_, and_

import oauth2, schemas, models
from database import get_db
import pandas as pd
import datetime, base64, logging
import os
import json
import dateparser
import backend_utils

router = APIRouter(prefix="/reports", tags=['reports'])
blogger = logging.getLogger('backend_logger')

@router.get('/filter_data')
def filter_data(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    course_name = [a for (a,) in db.query(models.Course.course_name).distinct().all()]
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
    for summary in summary_data:
        summary.video_names = json.loads(summary.video_names)
    return summary_data

@router.post('/download_summary_csv', status_code=status.HTTP_200_OK)
def download_summary_csv(params:schemas.SummaryQuery, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

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
                )
        .order_by(models.Summary.id.desc() 
                  )
        .all()
        )
    df_data = []
    for summary in summary_data:
        summary.video_names = json.loads(summary.video_names)
        df_data.append(summary.__dict__)

    df = pd.DataFrame(df_data)
    df.drop(columns=['_sa_instance_state'], inplace=True)
    df.rename(columns={'id':'summary_id'}, inplace=True)
    df = df[['date','summary_id','session_id','completed','start_time','end_time','room_number','course_name','total','present','absent','ratio','late_students','anger','disgust','fear','happy','neutral','sad','surprise','unknown', 'video_names']]
    return Response(content = df.to_csv(index=False), media_type="text/csv",
                    headers = { 'Content-Disposition': f'attachment; filename="result.csv"' } 
                    )

@router.post('/summary_data')
def summary_data(params:schemas.SummaryId, db: Session = Depends(get_db), 
                             current_user: int = Depends(oauth2.get_current_user)):

    student_alias = aliased(models.Student, name="student_details")

    emotion_data = (db.query(student_alias.thumbnail,
                            student_alias.first_name + ' ' + student_alias.last_name,
                            models.Emotion.student_id,
                            models.Emotion.is_present,
                            models.Emotion.anger,
                            models.Emotion.disgust,
                            models.Emotion.fear,
                            models.Emotion.happy,
                            models.Emotion.neutral,
                            models.Emotion.sad,
                            models.Emotion.surprise,
                            models.Emotion.unknown)
                            .join(student_alias,
                                    models.Emotion.student_id == student_alias.student_id)
                            .filter(models.Emotion.summary_id == params.summary_id)
                            .order_by(models.Emotion.student_id)
                            .all())

    data_out = []
    for data in emotion_data:
        data_out.append({
            'thumbnail': backend_utils.image_to_base64(data[0]) if data[0] != None else None,
            'student_name': data[1],
            'student_id': data[2],
            'is_present': data[3],
            'anger': data[4],
            'disgust': data[5],
            'fear':data[6],
            'happy':data[7],
            'neutral':data[8],
            'sad':data[9],
            'surprise':data[10],
            'unknown':data[11],
        })
    return data_out

@router.post('/download_summary_details_csv', status_code=status.HTTP_200_OK)
def download_summary_details_csv(params:schemas.SummaryId, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    student_alias = aliased(models.Student, name="student_details")
    emotion_data = (db.query(student_alias.first_name + ' ' + student_alias.last_name,
                            models.Emotion.student_id,
                            models.Emotion.is_present,
                            models.Emotion.anger,
                            models.Emotion.disgust,
                            models.Emotion.fear,
                            models.Emotion.happy,
                            models.Emotion.neutral,
                            models.Emotion.sad,
                            models.Emotion.surprise,
                            models.Emotion.unknown)
                            .join(student_alias,
                                    models.Emotion.student_id == student_alias.student_id)
                            .filter(models.Emotion.summary_id == params.summary_id)
                            .order_by(models.Emotion.student_id)
                            .all())

    columns = ['name', 'id', 'is_present', 'anger','disgust','fear','happy','neutral','sad','surprise','unknown']
    df = pd.DataFrame(emotion_data, columns=columns)
    
    return Response(content = df.to_csv(index=False), media_type="text/csv",
                    headers = { 'Content-Disposition': f'attachment; filename="result.csv"' } 
                    )

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
            'id':summary.id,
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
            'unknown':summary.unknown,
            'video_names': json.loads(summary.video_names)
        })        
    return response

@router.get('/get_live_class_summary', status_code=status.HTTP_200_OK)
def get_live_class_summary(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    live_sessions = (db.query(models.Summary.room_number, models.Summary.course_name, models.Summary.present, models.Summary.absent)
                    .filter(models.Summary.completed != True)
                    .all()
                    )
    return live_sessions

@router.get("/get_vid/{summary_id}")
async def get_video(summary_id: str):

    video_path = os.path.join('videos', f'{summary_id}.mp4')
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")
    print(video_path)
    def iterfile(video_path):
        with open(video_path, mode="rb") as video_file:
            video_file.seek(0)
            while True:
                chunk = video_file.read(8192)
                if not chunk:
                    break
                yield chunk
    return StreamingResponse(iterfile(video_path), media_type="video/mp4", headers={"Content-Disposition": "attechment; filename={summary_id}.mp4"})

@router.get("/get_video/{summary_id}&{video_filename}")
async def get_video(summary_id: str, video_filename: str):

    video_path = os.path.join('videos', summary_id, video_filename)
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")
    def iterfile(video_path):
        with open(video_path, mode="rb") as video_file:
            video_file.seek(0)
            while True:
                chunk = video_file.read(8192)
                if not chunk:
                    break
                yield chunk
    return StreamingResponse(iterfile(video_path), media_type="video/mp4", headers={"Content-Disposition": "attechment; filename={video_filename}.mp4"})