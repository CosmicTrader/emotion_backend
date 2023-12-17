from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, func, Boolean, Date, Time, Float
from sqlalchemy import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import MEDIUMBLOB

Base = declarative_base()

class User(Base):
    __tablename__ = 'user_details'
    timestamp = Column(TIMESTAMP, server_default=func.now())
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer,ForeignKey("user_details.id", ondelete='set null'), nullable = True)
    is_owner = Column(Boolean, nullable=False)
    is_admin = Column(Boolean, nullable=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    mobile_no = Column(String(20), nullable=True)
    image = Column(MEDIUMBLOB, nullable=True)

class Course(Base):
    __tablename__ = 'course_details'
    timestamp = Column(TIMESTAMP, server_default=func.now())
    id = Column(Integer, primary_key=True)

    course_id = Column(Integer, nullable= False, unique=True)
    course_name = Column(String(100), nullable= False)
    course_description = Column(String(1000), nullable= False)
    room_number = Column(Integer, nullable = True)
    start_time = Column(Time)
    end_time = Column(Time)

    enrollments = relationship('Enrollment', back_populates='course')

class Student(Base):
    __tablename__ = 'student_details'
    timestamp = Column(TIMESTAMP, server_default=func.now())
    id = Column(Integer, primary_key=True)

    student_id = Column(Integer, nullable = False, unique= True)
    first_name = Column(String(100), nullable= False)
    last_name = Column(String(100), nullable= False)
    email = Column(String(100), nullable=True, unique=True)
    mobile_no = Column(String(20), nullable=True)
    image = Column(MEDIUMBLOB, nullable=True)
    thumbnail = Column(MEDIUMBLOB, nullable=True)
    face_embeddings = Column(MEDIUMBLOB, nullable=True)

    enrollments = relationship('Enrollment', back_populates='student')

class Enrollment(Base):
    __tablename__ = 'enrollment_details'
    enrollment_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('student_details.student_id'))
    course_id = Column(Integer, ForeignKey('course_details.course_id'))

    student = relationship('Student', back_populates='enrollments')
    course = relationship('Course', back_populates='enrollments')

class Emotion(Base):
    __tablename__ = 'emotions'
    timestamp = Column(TIMESTAMP, server_default=func.now())
    id = Column(Integer, primary_key=True)
    summary_id = Column(Integer, ForeignKey('emotion_summary.id'))
    student_id = Column(Integer, nullable = False)
    subject = Column(String(100), nullable=True)
    anger = Column(Integer, nullable = True)
    disgust = Column(Integer, nullable = True)
    fear = Column(Integer, nullable = True)
    happy = Column(Integer, nullable = True)
    neutral = Column(Integer, nullable = True)
    sadness = Column(Integer, nullable = True)
    surprise = Column(Integer, nullable = True)
    unknown = Column(Integer, nullable = True)

    summary = relationship('Emotion_Summary', back_populates='summary_id')

class Emotion_Summary(Base):
    __tablename__ = 'emotion_summary'
    timestamp = Column(TIMESTAMP, server_default=func.now())
    id = Column(Integer, primary_key=True)
    room_number = Column(Integer, nullable = False)
    course_id = Column(Integer, nullable= False)
    course_name = Column(String(100), nullable= False)
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    total_students = Column(Integer, nullable= False)
    anger = Column(Integer, nullable = True)
    disgust = Column(Integer, nullable = True)
    fear = Column(Integer, nullable = True)
    happy = Column(Integer, nullable = True)
    neutral = Column(Integer, nullable = True)
    sadness = Column(Integer, nullable = True)
    surprise = Column(Integer, nullable = True)
    unknown = Column(Integer, nullable = True)
    
    summary_id = relationship('Emotion', back_populates='summary')

class Attendance(Base):
    __tablename__ = 'attendance'
    timestamp = Column(TIMESTAMP, server_default=func.now())
    id = Column(Integer, primary_key=True)
    summary_id = Column(Integer, ForeignKey('attendence_summary.id'))
    student_id = Column(Integer, nullable = False)
    is_present = Column(Boolean, nullable= False)

    summary = relationship('Attendence_Summary', back_populates='summary_id')

class Attendence_Summary(Base):
    __tablename__ = 'attendence_summary'
    timestamp = Column(TIMESTAMP, server_default=func.now())
    id = Column(Integer, primary_key=True)
    room_number = Column(Integer, nullable = False)
    course_id = Column(Integer, nullable= False)
    course_name = Column(String(100), nullable= False)
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    total_students = Column(Integer, nullable= False)
    present = Column(Integer, nullable= False)
    absent = Column(Integer, nullable= False)
    ratio = Column(Integer, nullable= False)

    summary_id = relationship('Attendance', back_populates='summary')
    
class Camera_Setting(Base):
    __tablename__ = 'camera_settings'
    timestamp = Column(TIMESTAMP, server_default=func.now())
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    camera_number = Column(Integer, nullable=False, unique=True)
    room_number = Column(Integer, nullable = False)
    name = Column(String(100))
    rtsp = Column(String(100))

    area = relationship("Area_Selection", back_populates="camera", passive_deletes=True)

class Area_Selection(Base):
    __tablename__ = 'area_selections'
    timestamp = Column(TIMESTAMP, server_default=func.now())
    id = Column(Integer, primary_key=True)
    user_id  = Column(Integer, nullable = False)
    camera_number = Column(Integer, ForeignKey('camera_settings.camera_number', ondelete='CASCADE'), nullable=False)
    model = Column(String(50))
    area = Column(String(5000))
    alert_start_time = Column(Time)
    alert_end_time = Column(Time)

    camera = relationship("Camera_Setting", back_populates="area")

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    date = Column(Date)
    time = Column(Time)
    camera_number = Column(Integer, nullable=False)
    wb_created = Column(Boolean)
    number_of_students = Column(Integer)
    avg_emotions = Column(String(500))

    image = relationship('Image', back_populates="event", passive_deletes=True)

class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'))
    image = Column(MEDIUMBLOB)

    event = relationship("Event", back_populates="image")

class Change(Base):
    __tablename__ = 'changes'
    id = Column(Integer, primary_key=True)
    camera_settings = Column(String(500))
    reset_counting = Column(String(500))

class Model(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    model_name = Column(String(50))
    threshold = Column(Float)

class Device_Detail(Base):
    __tablename__ = 'device_details'
    id = Column(Integer, primary_key = True)
    ip = Column(String(100))
    number_of_cameras = Column(Integer)

class Processing(Base):
    __tablename__ = 'processing'
    id = Column(Integer, primary_key = True)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    cameras = Column(Integer)
    time_taken = Column(Integer)
    frame_rate = Column(Float)
    average = Column(Float)
    frame_read = Column(Float)
    model = Column(Float)
    func = Column(Float)
    total = Column(Float)


# class Teacher(Base):
#     __tablename__ = 'teacher_details'
#     timestamp = Column(TIMESTAMP, server_default=func.now())
#     id = Column(Integer, primary_key=True)

#     teacher_id = Column(Integer, nullable=False, unique=True)
#     subject = Column(String(100), nullable= True)

#     class_id = Column(Integer, nullable = True)
#     first_name = Column(String(100), nullable= False)
#     last_name = Column(String(100), nullable= False)
#     email = Column(String(100), nullable=True, unique=True)
#     mobile_no = Column(String(20), nullable=True)
#     image = Column(MEDIUMBLOB, nullable=True)
#     thumbnail = Column(MEDIUMBLOB, nullable=True)
#     video_location = Column(String(500), nullable= True)
#     face_embeddings = Column(MEDIUMBLOB, nullable=True)

