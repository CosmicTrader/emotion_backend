from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func

import oauth2, schemas, models
from database import get_db
from backend_utils import reset_camera_counting, generate_pdf
import pandas as pd
import datetime, base64, logging
import dateparser

router = APIRouter(prefix="/courses", tags=['courses'])
blogger = logging.getLogger('backend_logger')

@router.post('/add_course', status_code=status.HTTP_201_CREATED)
def add_course(course_params: schemas.NewCourse, db: Session= Depends(get_db),
               current_user: int= Depends(oauth2.get_current_user)):
    
    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    course_registered = db.query(models.Courses).filter_by(course_id = course_params.course_id).first()

    if course_registered:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"Course-Id '{course_params.course_id}' is already registered"))

    course = models.Courses(**course_params.dict())
    db.add(course)
    db.commit()

    return True

@router.get('get_courses', status_code= status.HTTP_200_OK)
def get_courses(db: Session=Depends(get_db), current_user: int=Depends(oauth2.get_current_user)):

    try:
        courses = db.query(models.Courses.course_id, models.Courses.course_name).all()
        courses_list = [{'course_id': course.course_id, 'course_name': course.course_name} for course in courses]
        return courses_list
    except Exception as e:
            # Log the error or handle it appropriately
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post('/delete_course', status_code=status.HTTP_200_OK)
def delete_course(course_id: schemas.CoueseId, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    course = db.query(models.Courses).filter_by(course_id = course_id.course_id).first()

    if course :
        db.delete(course)
        db.commit()
        return True

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=(f"Requested Course not found"))

@router.post('add_students_to_course', status_code= status.HTTP_201_CREATED)
def add_students_to_course(students_data: schemas.CourseStudentData, db: Session= Depends(get_db), current_user: int= Depends(oauth2.get_current_user)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    course_registered = db.query(models.Courses).filter_by(course_id = students_data.course_id).first()

    if not course_registered:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"Course-Id '{students_data.course_id}' is not registered"))

    students = db.query(models.Student).filter(models.Student.student_id.in_(students_data.student_ids)).all()
    enrollments = [models.Enrollment(student= student, course= course_registered) for student in students]
    db.add_all(enrollments)
    db.commit()
    return f"Students assigned to course {students_data.course_id}"
