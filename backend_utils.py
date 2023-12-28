from passlib.context import CryptContext
import base64, json, cv2
import models
import numpy as np

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def base64_to_image(base64_data: str):
    return base64.b64decode(base64_data)

def image_to_base64(image):
    return base64.b64encode(image)

def make_static_image(camera_rtsp):

    if camera_rtsp == '0':
        camera_rtsp = 0

    cap = cv2.VideoCapture(camera_rtsp)
    ret,frame = cap.read()
    cap.release()
    if ret:
        frame = cv2.resize(frame, (416, 416))
        ret, buffer = cv2.imencode(".jpg", frame)
        if ret:
            return base64.b64encode(buffer)
        else:
            return False

def initialise_change(db):

    reset_state = models.Change(
        camera_settings = json.dumps([]),
        reset_counting = json.dumps([])
        )
    
    _change = db.query(models.Change).first()
    if _change:
        _change = reset_state
    else:
        db.add(reset_state)
    db.commit()
    return

def update_changes(camera_number, db):

    _change = db.query(models.Change).first()

    current_state = json.loads(_change.camera_settings)
    current_state.append(camera_number)
    _change.camera_settings = json.dumps(list(set(current_state)))
    db.commit()

    return

def get_ip(db):
    device_detail = db.query(models.Device_Detail).first()
    if device_detail:
        return device_detail.ip
    else:
        device_detail = models.Device_Detail(
            ip = '127.0.0.1',
            number_of_cameras = 5
            )
        db.add(device_detail)
        db.commit()
        return device_detail.ip

def get_images(image):
    if image == '':
        return None, None
    _image = base64_to_image(image)
    nparr = np.frombuffer(_image, np.uint8)

    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    resized_image = cv2.resize(image, (100,100), interpolation=cv2.INTER_AREA)
    thumbnail = cv2.imencode('.png', resized_image)[1]

    return _image, thumbnail

def generate_face_embeddings(images):
    
    
    return