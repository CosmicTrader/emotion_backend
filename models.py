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


class Courses(Base):
    __tablename__ = 'courses'
    timestamp = Column(TIMESTAMP, server_default=func.now())
    id = Column(Integer, primary_key=True)

    course_id = Column(Integer, unique=True, nullable= False)
    course_name = Column(String(100))
    course_description = Column(String(1000))

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
    __tablename__ = 'enrollments'
    enrollment_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('student_details.student_id'))
    course_id = Column(Integer, ForeignKey('courses.course_id'))

    student = relationship('Student', back_populates='enrollments')
    course = relationship('Courses', back_populates='enrollments')

# class Emotions(Base):
#     __tablename__ = 'emotions'
#     timestamp = Column(TIMESTAMP, server_default=func.now())
#     id = Column(Integer, primary_key=True)
#     student_id = Column(Integer, nullable = False)
#     class_id = Column(Integer, nullable = True)
#     subject = Column(String(100), nullable=True)
#     teacher_id = Column(String(100), ForeignKey("teacher_details.teacher_id", ondelete='set null'), nullable=True)
#     Anger = Column(Integer, nullable = True)
#     Disgust = Column(Integer, nullable = True)
#     Fear = Column(Integer, nullable = True)
#     Happy = Column(Integer, nullable = True)
#     Neutral = Column(Integer, nullable = True)
#     Sadness = Column(Integer, nullable = True)
#     Surprise = Column(Integer, nullable = True)
#     Unknown = Column(Integer, nullable = True)

# class Attendance(Base):
#     __tablename__ = 'emotions'
#     timestamp = Column(TIMESTAMP, server_default=func.now())
#     id = Column(Integer, primary_key=True)
#     student_id = Column(Integer, nullable = False)
#     class_id = Column(Integer, nullable = True)
#     camera_number = Column(Integer, nullable=True)
#     subject = Column(String(100), nullable=False)
#     teacher_id = Column(String(100), ForeignKey("teacher_details.teacher_id", ondelete='set null'), nullable=True)
#     lacture_starting_time = Column(Time)
#     lacture_ending_time = Column(Time)








class Camera_Settings(Base):
    __tablename__ = 'camera_settings'
    timestamp = Column(TIMESTAMP, server_default=func.now())
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    camera_number = Column(Integer, nullable=False, unique=True)
    name = Column(String(30))
    rtsp = Column(String(100))
    class_id = Column(String(100))

    area_selections = relationship("Area_Selection", back_populates="camera_settings", passive_deletes=True)

class Area_Selection(Base):
    __tablename__ = 'area_selection'
    timestamp = Column(TIMESTAMP, server_default=func.now())
    id = Column(Integer, primary_key=True)
    user_id  = Column(Integer, nullable = False)
    camera_number = Column(Integer, ForeignKey('camera_settings.camera_number', ondelete='CASCADE'), nullable=False)
    model = Column(String(50))
    area = Column(String(5000))
    alert_start_time = Column(Time)
    alert_end_time = Column(Time)
    camera_settings = relationship("Camera_Settings", back_populates="area_selections")

class Events(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    date = Column(Date)
    time = Column(Time)
    camera_number = Column(Integer, nullable=False)
    wb_created = Column(Boolean)
    number_of_students = Column(Integer)
    avg_emotions = Column(String(500))
    images = relationship('Images', back_populates="events", passive_deletes=True)

class Images(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'))
    image = Column(MEDIUMBLOB)
    events = relationship("Events", back_populates="images")

class Changes(Base):
    __tablename__ = 'changes'
    id = Column(Integer, primary_key=True)
    camera_settings = Column(String(500))
    reset_counting = Column(String(500))

class Models(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    model_name = Column(String(50))
    threshold = Column(Float)

class Device_Details(Base):
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
