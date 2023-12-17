from passlib.context import CryptContext
import base64, json, cv2
import models
from PIL import Image

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
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

def reset_camera_counting(camera_number, db):
    _change = db.query(models.Change).first()

    current_state = json.loads(_change.reset_counting)
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
        

def generate_face_embeddings(video):
    return


def create_thumbnail(image):
    if image == '' or None:
        return None
    try:
        with Image.open(image) as img:
            img.thumbnail((100,100))
            thumbnail_bytes = BytesIO()
            img.save(thumbnail_bytes, format='JPEG')
            return thumbnail_bytes.getvalue()
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None

def generate_pdf(event_list, headers):

    pdf = BytesIO()
    doc = SimpleDocTemplate(pdf,
                            pdfpagesize=letter,
                            leftMargin = 0,
                            rightMargin = 0,
                            topMargin = 10,
                            bottomMargin= 10 )
    elements = []
    styles = getSampleStyleSheet()

    table_data = [[a for a in headers.keys()]]
    col_widths = [a for a in headers.values()]

    for row in event_list:
        wrapped_row = []
        for i, cell in enumerate(row[:-1]):
            cell_content = str(cell)
            wrapped_cell = Paragraph(cell_content, styles['Normal'])
            wrapped_row.append(wrapped_cell)

        if row[-1]:
            nparr = np.frombuffer(row[-1], np.uint8)  # Convert binary data to NumPy array
            cv2_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # Decode the image using OpenCV
            resized_image = cv2.resize(cv2_image, (400, 400))
            resized_binary_image = cv2.imencode('.jpg', resized_image)[1].tobytes()
            wrapped_row.append(Image(BytesIO(resized_binary_image), width=100, height=100))

        table_data.append(wrapped_row)

    table = Table(table_data, rowHeights=110, repeatRows=1, colWidths=col_widths)

    style = TableStyle([
        # Column Headers Property
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey), #header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), #header
        ('BOTTOMPADDING', (0, 0), (-1, 0), 50),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        #table data property
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige), #table_data
        ('BOTTOMPADDING', (0, 1), (-2, -1), 40),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black)]
    )

    table.setStyle(style)
    elements.append(table)
    doc.build(elements)
    pdf.seek(0)

    return pdf