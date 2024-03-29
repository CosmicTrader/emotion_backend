from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
import os
from typing import List
from fastapi import Response, status, HTTPException, Depends, APIRouter, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, between, and_
import models, schemas, backend_utils, oauth2
from database import get_db, engine
import base64, logging, datetime, os
import shutil
import pandas as pd
import io
import zipfile
import pickle
import traceback

router = APIRouter(prefix="/students", tags=['Students'])
blogger = logging.getLogger('backend_logger')

weights_directory = os.path.join('weights')

@router.post('/add_student', status_code=status.HTTP_200_OK)
def student_registration(student_details: schemas.StudentRegistration, db: Session = Depends(get_db),
                         current_user: int = Depends(oauth2.get_current_user)):
    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    _id = db.query(models.Student).filter(
        models.Student.student_id == student_details.student_id).first()
    if _id:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"Id '{student_details.student_id}' is already registered"))

    email = db.query(models.Student).filter(
        models.Student.email == student_details.email).first()
    if email:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"Email-Id '{student_details.email}' is already registered"))

    new_student = models.Student(**student_details.dict(exclude={'video', 'images', 'image_names'}))
    if len(student_details.images) <= 4:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, 
                            detail= f'Please provide at least 5 photos.')

    photo_folder = os.path.join('photos', str(student_details.student_id))
    if not os.path.exists(photo_folder):
        os.mkdir(photo_folder)

    new_student.embeddings_generated = True
    new_student.image, new_student.thumbnail = backend_utils.get_images(student_details.image)
    new_student.date = datetime.datetime.today().strftime('%Y-%m-%d')
    new_student.video_path = os.path.join('photos',str(student_details.student_id))

    db.add(new_student)
    db.commit()

    return f'Student Registered.'


@router.post('/add_students_csv', status_code=status.HTTP_200_OK)
async def add_students_csv(file: UploadFile = File(...), db: Session = Depends(get_db),
                         current_user: int = Depends(oauth2.get_current_user)):
    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    registered_student = pd.read_sql_table('student_details', columns=['student_id','email'], index_col='id',con=engine)    
    
    data = await file.read()
    data = pd.read_csv(io.StringIO(data.decode()))
    data['registered'] = False
    data['Reason'] = None
    data['date'] = datetime.datetime.today().date()
    data['embeddings_generated'] = False
    data['video_path'] = None

    for i, row in data.iterrows():
        if row['student_id'] in registered_student['student_id']:
            data.loc[i, 'Reason'] = 'Student ID is already registered.'
        else:
            data.loc[i, 'registered'] = True
            data.loc[i, 'video_path'] = os.path.join('photos', str(row['student_id']))

    duplicate_emails = set(data['email']).intersection(set(registered_student['email']))

    duplicates = data[data['email'].isin(duplicate_emails)]
    for idx, row in duplicates.iterrows():
        data.loc[idx, 'registered'] = False
        data.loc[idx, 'Reason'] = 'Email ID is already registered.'

    res = data.drop(columns=['embeddings_generated','date','video_path'])
    res = res.to_csv(index=False)
    
    data = data[data['registered'] == True]
    data[['student_id','first_name','last_name','email','mobile_no', 'date']].to_sql('student_details', con=engine, index=False, if_exists='append')
    
    for i, row in data.iterrows():
        photo_folder = row['video_path']
        if not os.path.exists(photo_folder):
            os.mkdir(photo_folder)

    return Response(content = res, media_type="text/csv",
                    headers = { 'Content-Disposition': f'attachment; filename="result.csv"' } 
                    )

@router.post("/upload_photos/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db),
                      current_user: int = Depends(oauth2.get_current_user)):
    try:
        extraction_path = "zip"
        os.makedirs(extraction_path, exist_ok=True)

        file_path = os.path.join(extraction_path, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(extraction_path)
        os.remove(file_path)

        students = db.query(models.Student.student_id).all()
        student_ids = [str(s[0]) for s in students]

        students_data = []
        photo_data = []

        embedding_status = pd.DataFrame(students_data, columns=['student_id', 'status', 'error'])
        photo_status = pd.DataFrame(photo_data, columns=['student_id', 'image_name', 'status', 'error'])

        # Create Excel file with two sheets
        excel_bytes = io.BytesIO()
        with pd.ExcelWriter(excel_bytes, engine='xlsxwriter') as writer:
            embedding_status.to_excel(writer, sheet_name='Registration', index=False)
            photo_status.to_excel(writer, sheet_name='Photos', index=False)
        excel_bytes.seek(0)
        shutil.rmtree('zip')
        return StreamingResponse(content= excel_bytes, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={'Content-Disposition': 'attachment;filename=output.xlsx'})
    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse(content={"message": "Error processing the upload", "error": str(e)}, status_code=500)


@router.post('/delete_students', status_code=status.HTTP_202_ACCEPTED)
def delete_students(ids: schemas.StudentId, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    for student_id in ids.student_ids:
        student = db.query(models.Student).filter(
            models.Student.student_id == student_id).first()

        if student:
            db.delete(student)
    db.commit()
    return

@router.post('/students_by_session')
def students_by_session(session_id: schemas.SessionId, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    students_data = (db.query(models.Student.student_id, models.Student.first_name, models.Student.last_name,
                              models.Student.email, models.Student.thumbnail, models.Student.date)
                              .join(models.Enrollment)
                              .filter(models.Enrollment.session_id == session_id.session_id)
                              .all())

    students_out = []
    for student in students_data:
        students_out.append({
            'student_id' : student[0],
            'first_name':student[1],
            'last_name': student[2],
            'email':student[3],
            'thumbnail':backend_utils.image_to_base64(student[4]) if student[4] is not None else '',
            'date':student[5]
        })

    return students_out

@router.post('/students_by_date')
def students_by_date(params: schemas.StudentQuery, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    students_data = (db.query(models.Student.student_id,
                              models.Student.first_name,
                              models.Student.last_name,
                              models.Student.email,
                              models.Student.thumbnail,
                              models.Student.date)
                     .filter(models.Student.date >= params.start_date,
                             models.Student.date <= params.end_date)
                    .all()
                    )
    students_out = []
    for student in students_data:
        students_out.append({
            'student_id' : student[0],
            'first_name':student[1],
            'last_name': student[2],
            'email':student[3],
            'thumbnail':backend_utils.image_to_base64(student[4]) if student[4] is not None else '',
            'date':student[5]
        })
    return students_out


@router.post('/get_all_students')
def get_all_students(student_query: schemas.StudentQuery, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Not authorized to perform requested action')

    queries = []
    student_details = []
    if 0 not in student_query.room_numbers:
        queries.append(and_(models.Session.room_number.in_(student_query.room_numbers)))

    if 'all' not in student_query.courses:
        queries.append(and_(models.Enrollment.course_id.in_(student_query.courses)))

    if student_query.start_date != '':
        queries.append(and_(models.Student.date >= student_query.start_date))

    if student_query.end_date != '':
        queries.append(and_(models.Student.date <= student_query.end_date))

    if student_query.course_ ==  True:
        filtered_students = (
            db.query(models.Student,
                    func.group_concat(models.Enrollment.course_id).label('course_ids'),
                    func.group_concat(models.Session.room_number).label('room_numbers')
                    )
                    .join(models.Enrollment, models.Enrollment.student_id == models.Student.student_id)
                    .join(models.Course, models.Enrollment.course_id == models.Course.course_id)
                    .filter(*queries)
                    .group_by(models.Student.student_id)
                    .order_by(models.Student.date)
                    .all()
                    )

        for student, course_ids, room_numbers in filtered_students:
            _student = student.__dict__
            student_out = _student.copy()
            for a in _student:
                if a not in ['date','student_id','first_name','last_name', 'email','mobile_no', 'thumbnail']:
                    student_out.pop(a)
            student_out['thumbnail'] = base64.b64encode(student_out['thumbnail']).decode('utf-8') if student_out.get('thumbnail') != None else ''
            student_out['course_ids'] = list(map(int, course_ids.split(','))) if course_ids else []
            student_out['room_numbers'] = list(map(int, room_numbers.split(','))) if room_numbers else []  # Convert the string to a list of integers
            student_details.append(student_out)

        return student_details

    filtered_students = (
        db.query(models.Student)
                .join(models.Enrollment, models.Enrollment.student_id == models.Student.student_id)
                .join(models.Course, models.Enrollment.course_id == models.Course.course_id)
                .filter(*queries)
                .group_by(models.Student.student_id)
                .order_by(models.Student.date)
                .all()
                )

    for student in filtered_students:
        _student = student.__dict__
        student_out = _student.copy()
        for a in _student:
            if a not in ['date','student_id','first_name','last_name', 'email','mobile_no', 'thumbnail']:
                student_out.pop(a)
        student_out['thumbnail'] = base64.b64encode(student_out['thumbnail']).decode('utf-8') if student_out.get('thumbnail') != None else ''
        student_details.append(student_out)

    return student_details