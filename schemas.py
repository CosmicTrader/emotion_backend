from typing import List
from typing import Optional
from pydantic import BaseModel, EmailStr


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
    class_id : str
    class Config:
        orm_mode = True

class CameraOut(BaseModel):
    camera_number: int
    name: str
    rtsp: str
    ip_name: str
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
    video: Optional[str] = ''
    email: Optional[str] = ''
    mobile_no: Optional[str] = ''

class StudentQuery(BaseModel):
    course_: bool = True
    room_numbers: List[int]
    courses: List[str]
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

class SessionStudentData(BaseModel):
    course_id: int
    room_number: int
    start_date: str
    end_date: str
    start_time: str
    end_time: str
    student_ids: List[int]

class SessionId(BaseModel):
    session_id: int

class SummaryQuery(BaseModel):
    start_date: str
    end_date: str
    course_name: List[str]
    room_number: List[int]

class SummaryId(BaseModel):
    summary_id: int

class HomeSummary(BaseModel):
    date: str