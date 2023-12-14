from database import engine
from sqlalchemy.orm import Session
import models
import cv2
import models

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import numpy as np



def generate_pdf(event_list, location_mapper, name):

    pdf = name
    doc = SimpleDocTemplate(pdf,
                            pdfpagesize=letter,
                            leftMargin = 0,
                            rightMargin = 0,
                            topMargin = 10,
                            bottomMargin= 10 )
    elements = []
    styles = getSampleStyleSheet()

    table_data = [('Sr No', 'Camera Name', 'Speed', 'Alert', 'Time', 'Date', 'Vehicle', 'Location', 'Image')]  # Include the header row
    for row in event_list:
        wrapped_row = []
        for i, cell in enumerate(row[:-1]):
            cell_content = str(cell)
            wrapped_cell = Paragraph(cell_content, styles['Normal'])
            wrapped_row.append(wrapped_cell)

        location_content = str(location_mapper.get(row[1]))
        location_cell = Paragraph(location_content, styles['Normal'])
        wrapped_row.append(location_cell)

        nparr = np.frombuffer(row[-1], np.uint8)  # Convert binary data to NumPy array
        cv2_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # Decode the image using OpenCV
        resized_image = cv2.resize(cv2_image, (400, 400))
        resized_binary_image = cv2.imencode('.jpg', resized_image)[1].tobytes()
        wrapped_row.append(Image(BytesIO(resized_binary_image), width=100, height=100))

        table_data.append(wrapped_row)

    col_widths = [40, 70, 40, 50, 60, 70, 60, 60, 120]
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
    print(f'pdf generated for {name}')
    return


db= Session(engine)

query = db.query(models.Events)

total_events = query.count()
limit = 100
offset = 0

cameras = db.query(models.Events.camera_name).distinct().all()
locations = db.query(models.Camera_Settings).all()
locations = [loc.__dict__ for loc in locations]

location_mapper = {camera[0]: loc['ip_name'] for camera in cameras for loc in locations if loc['name'] == camera[0]}

while offset <= total_events:
    db_query = db.query(models.Events.id, models.Events.camera_name, models.Events.note, models.Events.event, models.Events.time, models.Events.date, 
                            models.Events.vehicle_category, models.Events.image).limit(limit)

    event_list = db_query.all()
    print('query completed')

    pdf_file = generate_pdf(event_list, location_mapper, f'{offset}.pdf')
    db_query = db.query(models.Events).order_by().limit(limit).all()
    for q in db_query:
        db.delete(q)
    db.commit()
    print('events deleted')

    offset += limit
