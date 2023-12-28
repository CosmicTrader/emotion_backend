from typing import List
from typing import Optional
from pydantic import BaseModel, EmailStr
import datetime

class Users(BaseModel):
    email: EmailStr
    password: str

class UserRegistration(BaseModel):
    name: str
    email: EmailStr
    password: str
    mobile_no: str
    is_owner: bool
    image: Optional[str] = ''
    is_admin: Optional[bool] = False

class UserOut(BaseModel):
    email: EmailStr
    name: str
    mobile_no: str
    date: str
    image: Optional[str] = ''
    is_owner: bool
    is_admin: bool
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    image: bytes
    is_owner: bool
    is_admin: bool

class TokenData(BaseModel):
    id: Optional[str] = None

class AddCamera(BaseModel):
    camera_number: int
    name: str
    rtsp: str
    room_number : int
    class Config:
        orm_mode = True

class CameraOut(BaseModel):
    camera_number: int
    name: str
    rtsp: str
    room_number: str
    class Config:
        orm_mode = True


class Email(BaseModel):
    email: str

class CameraNumber(BaseModel):
    camera_number: int

class StudentRegistration(BaseModel):
    student_id: int
    first_name: str
    last_name: str
    image: Optional[str] = ''
    images: List[Optional[str]] = []
    email: Optional[str] = ''
    mobile_no: Optional[str] = ''

class StudentQuery(BaseModel):
    course_: Optional[bool] = True
    room_numbers: Optional[List[int]]
    courses: Optional[List[str]]
    start_date: Optional[str] = ''
    end_date: Optional[str] = ''

class StudentId(BaseModel):
    student_ids: List[int]

class Course(BaseModel):
    course_id: int
    course_name: str
    course_description: str

class CourseName(BaseModel):
    course_name: str

class SessionData(BaseModel):
    course_name: str
    room_number: int
    start_date: str
    end_date: str
    start_time: str
    end_time: str
    session_id: str
    student_ids: List[int]

class SessionId(BaseModel):
    session_id: int

class SummaryQuery(BaseModel):
    start_date: Optional[str] = datetime.datetime.today().date()
    end_date: Optional[str] = datetime.datetime.today().date()
    start_time: Optional[str]= '00:00'
    end_time: Optional[str] = '23:59'
    course_name: Optional[str]
    room_number: Optional[int]
    session_id: Optional[int]
    # course_name: List[str]
    # room_number: List[int]
    # session_id: List[int]

class SummaryId(BaseModel):
    summary_id: int

class HomeSummary(BaseModel):
    date: str