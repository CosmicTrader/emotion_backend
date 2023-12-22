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
def add_course(course_params: schemas.Course, db: Session= Depends(get_db),
               current_user: int= Depends(oauth2.get_current_user)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    course_registered = db.query(models.Course).filter_by(course_id = course_params.course_id).first()

    if course_registered:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"Course-Id '{course_params.course_id}' is already registered"))

    course_params = course_params.dict()
    if course_params['start_time'] == '':
        del course_params['start_time']

    if course_params['end_time'] == '':
        del course_params['end_time']

    if course_params['room_number'] == -1:
        del course_params['room_number']

    course = models.Course(**course_params)
    db.add(course)
    db.commit()

    return True

@router.post('/edit_course', status_code=status.HTTP_201_CREATED)
def edit_course(course_params: schemas.Course, db: Session= Depends(get_db),
               current_user: int= Depends(oauth2.get_current_user)):
    
    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    course_registered = db.query(models.Course).filter_by(course_id = course_params.course_id).first()

    if not course_registered:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"Course-Id '{course_params.course_id}' is not registered"))

    course_params = course_params.dict()
    course_registered.course_name = course_params.course_name
    course_registered.course_description = course_params.course_description

    if course_params['start_time'] == '':
        del course_params['start_time']
    else:
        course_registered.start_time = course_params['start_time']
    
    if course_params['end_time'] == '':
        del course_params['end_time']
    else:
        course_registered.end_time = course_params['end_time']
    
    if course_params['room_number'] == -1:
        del course_params['room_number']
    else:
        course_registered.room_number = course_params['room_number']
    db.commit()

    return True

@router.get('get_courses', status_code= status.HTTP_200_OK)
def get_courses(db: Session=Depends(get_db), current_user: int=Depends(oauth2.get_current_user)):

    try:
        courses = db.query(models.Course).all()
        courses_list = [{'created_at': course.date,
                         'course_id': course.course_id,
                         'name': course.course_name,
                         'description': course.course_description,
                         'room_number': course.room_number,
                         'start_time': course.start_time,
                         'end_time': course.end_time
                        }for course in courses ]
        return courses_list
    except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post('/delete_course', status_code=status.HTTP_200_OK)
def delete_course(course_id: schemas.CoueseId, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    course = db.query(models.Course).filter_by(course_id = course_id.course_id).first()

    if course :
        db.delete(course)
        db.commit()
        return True

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=(f"Requested Course not found"))

@router.post('add_students_to_course', status_code= status.HTTP_201_CREATED)
def add_students_to_course(course_params: schemas.CourseStudentData, db: Session= Depends(get_db), current_user: int= Depends(oauth2.get_current_user)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    registered_course = db.query(models.Course).filter_by(course_id = course_params.course_id).first()

    if not registered_course:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"Course-Id '{course_params.course_id}' is not registered"))


    if course_params.start_time == '':
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"Start Time '{course_params.start_time}' is not valid"))
    else:
        registered_course.start_time = course_params.start_time
    
    if course_params.end_time == '':
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"End Time '{course_params.end_time}' is not valid"))
    else:
        registered_course.end_time = course_params.end_time
    
    if course_params.room_number == -1:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"Room Number '{course_params.room_number}' is not valid"))
    else:
        registered_course.room_number = course_params.room_number

    existing_enrollments = db.query(models.Enrollment).filter(
            models.Enrollment.student_id.in_(course_params.student_ids),
            models.Enrollment.course_id == course_params.course_id
        ).all()

    existing_student_ids = {enrollment.student_id for enrollment in existing_enrollments}

    new_enrollments = [
        models.Enrollment(student_id=student_id, course_id=course_params.course_id)
        for student_id in course_params.student_ids
        if student_id not in existing_student_ids
    ]

    db.add_all(new_enrollments)
    db.commit()
    return {"new": len(new_enrollments),
            "course_name": registered_course.course_name,
            "total": len(new_enrollments) + len(existing_student_ids)
            }
