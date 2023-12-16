from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import datetime
import models, schemas, backend_utils, oauth2
from database import get_db
import base64, logging

router = APIRouter(prefix="/students", tags=['Students'])
blogger = logging.getLogger('backend_logger')

@router.post('/add_student', status_code=status.HTTP_201_CREATED)
def student_registration(student_details: schemas.StudentRegistration, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

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

    student_details.image = backend_utils.base64_to_image(student_details.image) if student_details.image != '' else None
    student_details.video = backend_utils.generate_face_embeddings(student_details.video) if student_details.video != '' else None
    new_student = models.Student(**student_details.dict(exclude={'video'}))
    new_student.thumbnail = backend_utils.create_thumbnail(new_student.image) if new_student.image != None or '' else None

    db.add(new_student)
    db.commit()

    return

@router.post('/delete_students', status_code=status.HTTP_202_ACCEPTED)
def delete_students(ids: schemas.StudentId, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    for student_id in ids.student_ids:
        student = db.query(models.Student).filter(
            models.Student.student_id == student_id).first()
        print(student)

        if student:
            db.delete(student)
    db.commit()
    return

@router.post('/get_all_students')
def get_students(student_query: schemas.StudentQuery, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Not authorized to perform requested action')

    filter_conditions = []

    if 0 not in student_query.class_ids:
        filter_conditions.append(models.Student.class_id.in_(student_query.class_ids))

    if 'all' not in  student_query.streams:
        filter_conditions.append(models.Student.stream.in_(student_query.streams))

    if 'all' not in  student_query.date_added:
        date_added_conditions = [func.DATE(models.Student.timestamp) == datetime.strptime(date, "%Y-%m-%d").date() for date in student_query.date_added]
        filter_conditions.append(or_(*date_added_conditions))

    filtered_students = db.query(models.Student).filter(*filter_conditions).all()

    student_details = []
    for student in filtered_students:
        _student = student.__dict__
        student_out = _student.copy()
        for a in _student:
            if a not in ['student_id','standard','stream','class_id','first_name','last_name','email','mobile_no','thumbnail']:
                student_out.pop(a)
        student_out['thumbnail'] = base64.b64encode(student_out['thumbnail']).decode('utf-8') if student_out['thumbnail'] != None else ''
        student_details.append(student_out)

    return student_details
