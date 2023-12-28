from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, func, Boolean, Date, Time, Float, DateTime
from sqlalchemy import func
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.mysql import MEDIUMBLOB

Base = declarative_base()


class User(Base):
    __tablename__ = 'user_details'
    date = Column(Date)
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
    date = Column(Date)
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, nullable= False, unique=True)
    course_name = Column(String(100), nullable= False, unique=True)
    course_description = Column(String(1000), nullable= False)
    
    enrollments = relationship('Enrollment', back_populates='course')

class Session(Base):
    __tablename__ = 'session_details'
    date = Column(Date)
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, nullable= False, unique=True)
    course_name = Column(String(100), nullable= False)
    course_description = Column(String(1000), nullable= False)
    room_number = Column(Integer, nullable = True)
    start_date = Column(Date)
    end_date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)

    enrollments = relationship('Enrollment', back_populates='session')

class Student(Base):
    __tablename__ = 'student_details'
    date = Column(Date)
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, nullable = False, unique= True)
    first_name = Column(String(100), nullable= False)
    last_name = Column(String(100), nullable= False)
    email = Column(String(100), nullable=True, unique=True)
    mobile_no = Column(String(20), nullable=True)
    image = Column(MEDIUMBLOB, nullable=True)
    thumbnail = Column(MEDIUMBLOB, nullable=True)
    face_embeddings = Column(MEDIUMBLOB, nullable=True)
    embeddings_generated = Column(Boolean)
    video_path = Column(String(1000))

    enrollments = relationship('Enrollment', back_populates='student')

class Enrollment(Base):
    __tablename__ = 'enrollment_details'
    enrollment_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('student_details.student_id'))
    course_id = Column(Integer, ForeignKey('course_details.course_id'))
    session_id = Column(Integer, ForeignKey('session_details.session_id'))

    student = relationship('Student', back_populates='enrollments')
    course = relationship('Course', back_populates='enrollments')
    session = relationship('Session', back_populates='enrollments')

class Emotion(Base):
    __tablename__ = 'emotions'
    timestamp = Column(TIMESTAMP, server_default=func.now())
    id = Column(Integer, primary_key=True)
    summary_id = Column(Integer, ForeignKey('summary.id'))
    student_id = Column(Integer, nullable = False)
    is_present = Column(Boolean, nullable= False)
    anger = Column(Integer, nullable = True)
    disgust = Column(Integer, nullable = True)
    fear = Column(Integer, nullable = True)
    happy = Column(Integer, nullable = True)
    neutral = Column(Integer, nullable = True)
    sad = Column(Integer, nullable = True)
    surprise = Column(Integer, nullable = True)
    unknown = Column(Integer, nullable = True)

    summary = relationship('Summary', back_populates='emotion_id')

class Attendance(Base):
    __tablename__ = 'attendance'
    timestamp = Column(TIMESTAMP, server_default=func.now())
    id = Column(Integer, primary_key=True)
    summary_id = Column(Integer, ForeignKey('summary.id'))
    student_id = Column(Integer, nullable = False)
    is_present = Column(Boolean, nullable= False)

    summary = relationship('Summary', back_populates='attendance_id')

class Summary(Base):
    __tablename__ = 'summary'
    date = Column(Date)
    id = Column(Integer, primary_key=True)
    room_number = Column(Integer, nullable = False)
    session_id = Column(Integer, nullable= False)
    course_name = Column(String(100), nullable= False)
    completed = Column(Boolean)
    start_time = Column(Time)
    end_time = Column(Time)
    total = Column(Integer, nullable= False)
    present = Column(Integer, nullable= False)
    absent = Column(Integer, nullable= False)
    ratio = Column(Integer, nullable= False)
    anger = Column(Integer, nullable = True)
    disgust = Column(Integer, nullable = True)
    fear = Column(Integer, nullable = True)
    happy = Column(Integer, nullable = True)
    neutral = Column(Integer, nullable = True)
    sad = Column(Integer, nullable = True)
    surprise = Column(Integer, nullable = True)
    unknown = Column(Integer, nullable = True)
    
    emotion_id = relationship('Emotion', back_populates='summary')
    attendance_id = relationship('Attendance', back_populates='summary')

class Camera_Setting(Base):
    __tablename__ = 'camera_settings'
    date = Column(Date)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    camera_number = Column(Integer, nullable=False, unique=True)
    room_number = Column(Integer, nullable = False)
    name = Column(String(100))
    rtsp = Column(String(100))

class Change(Base):
    __tablename__ = 'changes'
    id = Column(Integer, primary_key=True)
    camera_settings = Column(String(500))
    reset_counting = Column(String(500))

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