from typing import List
from datetime import datetime
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
    timestamp: datetime
    image: Optional[str] = ''
    is_owner: bool
    is_admin: bool

    class Config:
        orm_mode = True

class StudentRegistration(BaseModel):
    class_id: int
    student_id: int
    first_name: str
    last_name: str
    standard: Optional[str] = ''
    stream: Optional[str] = ''
    image: Optional[str] = ''
    video: Optional[str] = ''
    email: Optional[str] = ''
    mobile_no: Optional[str] = ''


class TeacherRegistration(BaseModel):
    class_id: int
    teacher_id: int
    first_name: str
    last_name: str
    subject: Optional[str] = ''
    image: Optional[str] = ''
    video: Optional[str] = ''
    email: Optional[str] = ''
    mobile_no: Optional[str] = ''

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    image: bytes
    is_owner: bool
    is_admin: bool


class TokenData(BaseModel):
    id: Optional[str] = None

class AreaSelection(BaseModel):
    
    camera_number: int
    assign: list

    class Config:
        orm_mode = True

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

class EventCount(BaseModel):
    event: Optional[str] = None
    date: Optional[str] = None
    end_date: Optional[str] = None
    
class EventPage(BaseModel):
    event: str
    date: str
    page_number: int
    page_size: int


class StudentQuery(BaseModel):
    class_ids: List[int]
    streams: List[str]
    date_added: List[str]

class Email(BaseModel):
    email: str

class StudentId(BaseModel):
    student_ids: List[int]

class CameraNumber(BaseModel):
    camera_number: int