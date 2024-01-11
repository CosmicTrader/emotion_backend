from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func

import oauth2, schemas, models
from database import get_db
import logging, datetime
from backend_utils import update_change_in_session, update_change_in_course

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
        update_change_in_course(course_name= course_params.course_name, db= db)
        db.commit()
        return {'message': f'Details for course name "{course_params.course_name}" update successfully'}

    course = models.Course(**course_params.dict())
    course.date = datetime.datetime.today().date()
    db.add(course)
    update_change_in_course(course_name= course_params.course_name, db= db)
    db.commit()

    return True

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

@router.post('/delete_course', status_code=status.HTTP_200_OK)
def delete_course(course_name: schemas.CourseName, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    course = db.query(models.Course).filter_by(course_name = course_name.course_name).first()

    if course :
        db.delete(course)
        update_change_in_course(course_name= course_name.course_name, db= db)

        db.commit()
        return True

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=(f"Requested Course not found"))

@router.post('/create_session', status_code= status.HTTP_201_CREATED)
def create_session(params: schemas.SessionData, db: Session= Depends(get_db), current_user: int= Depends(oauth2.get_current_user)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    registered_course = db.query(models.Course).filter_by(course_name = params.course_name).first()

    if not registered_course:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"Course-Name '{params.course_name}' is not registered"))

    if params.start_time == '':
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"Start Time '{params.start_time}' is not valid"))

    if params.end_time == '':
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"End Time '{params.end_time}' is not valid"))

    if params.start_date == '':
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"Start Time '{params.start_date}' is not valid"))

    if params.end_date == '':
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"End Time '{params.end_date}' is not valid"))

    if params.room_number == -1:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"Room Number '{params.room_number}' is not valid"))

    # session = db.query(models.Session).filter_by(room_number = params.room_number, course_name = params.course_name).all()
    # if len(session) > 0:
    #     for ses in session:
    #         if params.start_time < ses.end_time:
    #             pass

    session = db.query(models.Session).filter_by(session_id = params.session_id).first()
    if session:
        session.course_id = registered_course.course_id
        session.course_name = registered_course.course_name
        session.course_description = registered_course.course_description
        session.start_date = params.start_date
        session.end_date = params.end_date
        session.start_time = params.start_time
        session.end_time = params.end_time
    else:
        session = models.Session(**params.dict(exclude={'student_ids'}))
        session.course_id = registered_course.course_id
        session.date = datetime.datetime.today().date()
        session.course_name = registered_course.course_name
        session.course_description = registered_course.course_description
        db.add(session)

    db.commit()
    db.refresh(session)

    existing_enrollments = (db.query(models.Enrollment)
                            .filter(models.Enrollment.session_id == params.session_id,
                                    # models.Enrollment.student_id.in_(params.student_ids)
                                    )
                            .all())
    existing_student_ids = [enrollment.student_id for enrollment in existing_enrollments]

    delete_list = [a for a in existing_student_ids if a not in params.student_ids]

    db.query(models.Enrollment).filter(models.Enrollment.student_id.in_(delete_list),
                                       models.Enrollment.session_id == params.session_id).delete()

    new_enrollments = [models.Enrollment(student_id = student_id,
                                         course_id  = registered_course.course_id,
                                         session_id = session.session_id
                                         )
                       for student_id in params.student_ids if student_id not in existing_student_ids
                       ]

    db.add_all(new_enrollments)

    update_change_in_session(session_id= params.session_id, db= db)

    db.commit()

    return {"new": len(new_enrollments),
            "course_name": registered_course.course_name,
            "delete":len(delete_list),
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

        for session in session_list:
            students = db.query(models.Enrollment.student_id).filter_by(session_id = session['session_id']).all()
            session['students'] = [a for (a,) in students]

        return session_list

    except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post('/edit_session', status_code=status.HTTP_200_OK)
def edit_session(params: schemas.EditSession, db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):
    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))
    
    existing_session = db.query(models.Enrollment).filter_by(session_id = params.session_id).first()

    existing_enrollments = db.query(models.Enrollment).filter(models.Enrollment.session_id == params.session_id).all()
    existing_student_ids = [enrollment.student_id for enrollment in existing_enrollments]

    delete_list = [a for a in existing_student_ids if a not in params.student_ids]

    db.query(models.Enrollment).filter(models.Enrollment.student_id.in_(delete_list),
                                       models.Enrollment.session_id == 2).delete()

    new_enrollments = [models.Enrollment(student_id=student_id,
                                         course_id=existing_session.course_id,
                                         session_id=existing_session.session_id
                                         )
                       for student_id in params.student_ids if student_id not in existing_student_ids
                       ]

    db.add_all(new_enrollments)

    update_change_in_session(session_id= params.session_id, db= db)

    db.commit()

    return {"new": len(new_enrollments),
            "delete":len(delete_list),
            "total": len(new_enrollments) + len(existing_student_ids)
            }

@router.post('/delete_session', status_code=status.HTTP_200_OK)
def delete_session(session_id: schemas.SessionId, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    session = db.query(models.Session).filter_by(session_id = session_id.session_id).first()

    if session :
        db.delete(session)
        update_change_in_session(session_id= session_id.session_id, db= db)
        db.commit()

        return True

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=(f"Requested Session not found"))

