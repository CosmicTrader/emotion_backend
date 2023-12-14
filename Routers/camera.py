import json, datetime, logging

from fastapi import APIRouter, Depends, Response, status, HTTPException, Cookie
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session
from sqlalchemy import select

import oauth2, schemas, models
from database import get_db
from backend_utils import image_to_base64, make_static_image, update_changes

router = APIRouter(prefix="/camera", tags=['camera_settings'])
blogger = logging.getLogger('backend_logger')

@router.post('/Areaselection', status_code=status.HTTP_201_CREATED)
def assign_area(area_selection_settings: schemas.AreaSelection,
                db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    def add_model(area_selection_settings):
        all_area_selection = area_selection_settings.dict()
        _models = []
        for area_selection in all_area_selection['assign'] :
            new_area_selection = {}
            
            new_area_selection['camera_number'] = all_area_selection['camera_number']
            new_area_selection['user_id'] = current_user.id
            new_area_selection['model'] = area_selection['model']
            new_area_selection['direction'] = area_selection['direction'] if area_selection.get('direction') else 'up'

            new_area_selection['alert_start_time'] = datetime.datetime.strptime(area_selection['alert_start_time'], '%H:%M')
            new_area_selection['alert_end_time'] = datetime.datetime.strptime(area_selection['alert_end_time'], '%H:%M')
            
            area_selection_model = models.Area_Selection(**new_area_selection)
            _models.append(area_selection_model)

        db.add_all(_models)
        db.commit()

        update_changes(camera_number = all_area_selection['camera_number'],  db = db)

    existing_area = db.query(models.Area_Selection).filter_by(
        camera_number = area_selection_settings.camera_number).all()

    if existing_area:
        for area in existing_area:
            db.delete(area)
            db.commit()

        add_model(area_selection_settings)

        return 'Models updated for the selected camera'

    else :
        add_model(area_selection_settings)

        return 'Models added for the selected camera'

@router.post('/delete_area_settings', status_code=status.HTTP_200_OK)
def delete_area_settings(camera_number: schemas.CameraNumber,
                         db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    area_selection_to_delete = db.query(models.Area_Selection).filter_by(
        camera_number = camera_number.camera_number).first()

    if area_selection_to_delete:
        db.delete(area_selection_to_delete)
        db.commit()

        update_changes(camera_number= camera_number.camera_number, db = db)
        return True

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=(
            f"Requested camera details not found"))

@router.get('/get_model_settings')
def get_model_settings(db: Session=Depends(get_db), current_user: int=Depends(oauth2.get_current_user)):
    blogger.error('sending model settings')
    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    all_models = db.query(models.Area_Selection).all()

    model_details = [m.__dict__ for m in all_models]
    
    output = []
    for item in model_details:
        camera_number = item['camera_number']

        item['area'] = json.loads(item['area'])
        if len(item['area']) > 0:
            for area in item['area'][0]:
                area[0] = round(float(area[0])/416,3)
                area[1] = round(float(area[1])/416,3)
        item['area'] = json.dumps(item['area'])

        assign = {"model": item['model'], "alert_start_time": str(item['alert_start_time'])[0:5], 
                  "alert_end_time": str(item['alert_end_time'])[0:5], "area": item['area'], 
                  }
        found = False
        for i, result in enumerate(output):
            if result['camera_number'] == camera_number:
                found = True
                output[i]['assign'].append(assign)
        if not found:
            output.append({"camera_number": camera_number, "assign": [assign]})

    return output


@router.get('/model_names')
def get_model_names(db:Session = Depends(get_db), current_user: int=Depends(oauth2.get_current_user)):

    names = db.query(models.Models).all()
    names = [n.__dict__ for n in names]
    model_names = [{'model_name':n['model_name']} for n in names]
    
    return json.dumps(model_names)

@router.post('/addcamera', status_code=status.HTTP_201_CREATED)
def add_camera(camera_details: schemas.AddCamera, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    existing_camera = db.query(models.Camera_Settings).filter_by(camera_number=camera_details.camera_number).first()
    
    if existing_camera:
        existing_camera.rtsp = camera_details.rtsp
        existing_camera.name = camera_details.name
        existing_camera.class_id = camera_details.class_id

        db.commit()

        update_changes(camera_number= camera_details.camera_number, db = db)
        return {"message": f"Details for camera number {camera_details.camera_number} updated successfully"}

    else:
        number_of_cameras = len(db.query(models.Camera_Settings).all())
        max_number_of_cameras = db.query(models.Device_Details).first().number_of_cameras
        if number_of_cameras >= max_number_of_cameras:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail = f"Camera limit of {max_number_of_cameras} has been reached")

        new_camera = camera_details.__dict__
        new_camera['user_id'] = current_user.id

        camera = models.Camera_Settings(**new_camera)
        db.add(camera)
        db.commit()
        db.refresh(camera)

        update_changes(camera_number = camera_details.camera_number, db = db)
        return camera

@router.post('/delete_camera', status_code=status.HTTP_200_OK)
def delete_camera(camera_number: schemas.CameraNumber, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    camera = db.query(models.Camera_Settings).filter_by(camera_number = camera_number.camera_number).first()

    if camera :
        db.delete(camera)
        db.commit()

        update_changes(camera_number = camera_number.camera_number, db = db)
        return True

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=(f"Requested camera details not found"))

@ router.get('/get_cameras')
def get_camera_details(db: Session=Depends(get_db), current_user: int=Depends(oauth2.get_current_user)):

    cameras=db.query(models.Camera_Settings).all()
    
    camera_details=[]
    for camera in cameras:
        cam = camera.__dict__
        camera_out = cam.copy()
        for a in cam:
            if a not in ['camera_number', 'assign', 'name', 'rtsp', 'class_id']:
                camera_out.pop(a)

        camera_details.append(camera_out)

    return camera_details


@ router.post('/get_camera_image')
def get_camera_image(camera_number: schemas.CameraNumber, current_user: int=Depends(oauth2.get_current_user),
                      db: Session=Depends(get_db)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    camera_details = db.query(models.Camera_Settings).\
                        filter_by(camera_number=int(camera_number.camera_number)).first()
    
    if camera_details:
        camera_details = camera_details.__dict__

        frame = make_static_image(camera_details['rtsp'])
        if frame:
            return frame
        else:
            return f"Could not get camera feed from {camera_details['name']}."
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=(
            f"There is no camera with number {camera_number.camera_number}"))