from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func

import oauth2, schemas, models
from database import get_db
import logging, datetime

router = APIRouter(prefix="/courses", tags=['courses'])
blogger = logging.getLogger('backend_logger')

@router.post('/add_course', status_code=status.HTTP_201_CREATED)
def add_course(course_params: schemas.Course, db: Session= Depends(get_db),
               current_user: int= Depends(oauth2.get_current_user)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    _course = db.query(models.Course).filter_by(course_name = course_params.course_name).first()

    if _course:
        _course.course_name = course_params.course_name
        _course.course_description = course_params.course_description
        _course.date = datetime.datetime.today().date()
        db.commit()
        return {'message': f'Details for course name "{course_params.course_name}" update successfully'}

    course = models.Course(**course_params.dict())
    course.date = datetime.datetime.today().date()
    db.add(course)
    db.commit()

    return True

@router.post('/delete_course', status_code=status.HTTP_200_OK)
def delete_course(course_name: schemas.CourseName, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    course = db.query(models.Course).filter_by(course_name = course_name.course_name).first()

    if course :
        db.delete(course)
        db.commit()
        return True

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=(f"Requested Course not found"))

@router.get('/get_course', status_code= status.HTTP_200_OK)
def get_courses(db: Session=Depends(get_db), current_user: int=Depends(oauth2.get_current_user)):

    try:
        courses = db.query(models.Course).all()
        courses_list = [{'created_at': course.date,
                         'course_id': course.course_id,
                         'course_name': course.course_name,
                         'course_description': course.course_description,
                        }
                        for course in courses 
                        ]
        return courses_list
    except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post('create_session', status_code= status.HTTP_201_CREATED)
def create_session(course_params: schemas.SessionStudentData, db: Session= Depends(get_db), current_user: int= Depends(oauth2.get_current_user)):

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
    new_enrollments = [models.Enrollment(student_id=student_id, course_id=course_params.course_id)
                       for student_id in course_params.student_ids
                       if student_id not in existing_student_ids
                       ]
    db.add_all(new_enrollments)
    db.commit()

    return {"new": len(new_enrollments),
            "course_name": registered_course.course_name,
            "total": len(new_enrollments) + len(existing_student_ids)
            }

@router.get('/get_session', status_code= status.HTTP_200_OK)
def get_session(db: Session=Depends(get_db), current_user: int=Depends(oauth2.get_current_user)):

    try:
        sessions = db.query(models.Session).all()
        session_list = [{'created_at': session.date,
                         'session_id': session.session_id,
                         'course_name': session.course_name,
                         'course_description': session.course_description,
                         'room_number': session.room_number,
                         'start_date': session.start_date,
                         'end_date': session.end_date,
                         'start_time': session.start_time,
                         'end_time': session.end_time,
                         'students': []
                        }for session in sessions ]

        return session_list
    except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post('/delete_session', status_code=status.HTTP_200_OK)
def delete_session(session_id: schemas.SessionId, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    session = db.query(models.Session).filter_by(session_id = session_id.session_id).first()

    if session :
        db.delete(session)
        db.commit()
        return True

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=(f"Requested Session not found"))
