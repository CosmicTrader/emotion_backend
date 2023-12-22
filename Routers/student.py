from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, between, and_
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

    # image, thumbnail = backend_utils.get_images(student_details.image)
    student_details.image = backend_utils.base64_to_image(student_details.image) if student_details.image != '' else None
    student_details.video = backend_utils.generate_face_embeddings(student_details.video) if student_details.video != '' else None
    new_student = models.Student(**student_details.dict(exclude={'video'}))
    new_student.thumbnail = backend_utils.create_thumbnail(new_student.image) if new_student.image != None or '' else None
    new_student.date = datetime.datetime.today().strftime('%Y-%m-%d')

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

    queries = []
    student_details = []
    
    if 0 not in student_query.room_numbers:
        queries.append(and_(models.Course.room_number.in_(student_query.room_numbers)))

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
                     func.group_concat(models.Course.room_number).label('room_numbers')
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
                if a not in ['date','student_id','first_name','last_name', 'email','mobile_no']:
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
            if a not in ['date','student_id','first_name','last_name', 'email','mobile_no']:
                student_out.pop(a)
        student_out['thumbnail'] = base64.b64encode(student_out['thumbnail']).decode('utf-8') if student_out.get('thumbnail') != None else ''
        student_details.append(student_out)

    return student_details

    