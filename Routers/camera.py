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


@router.post('/addcamera', status_code=status.HTTP_201_CREATED)
def add_camera(camera_details: schemas.AddCamera, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    existing_camera = db.query(models.Camera_Setting).filter_by(camera_number=camera_details.camera_number).first()
    
    if existing_camera:
        existing_camera.rtsp = camera_details.rtsp
        existing_camera.name = camera_details.name
        existing_camera.room_number = camera_details.room_number

        db.commit()

        update_changes(camera_number= camera_details.camera_number, db = db)
        return {"message": f"Details for camera number {camera_details.camera_number} updated successfully"}

    else:
        number_of_cameras = len(db.query(models.Camera_Setting).all())
        max_number_of_cameras = db.query(models.Device_Detail).first().number_of_cameras
        if number_of_cameras >= max_number_of_cameras:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail = f"Camera limit of {max_number_of_cameras} has been reached")

        new_camera = camera_details.__dict__
        new_camera['user_id'] = current_user.id

        camera = models.Camera_Setting(**new_camera)
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

    camera = db.query(models.Camera_Setting).filter_by(camera_number = camera_number.camera_number).first()

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

    cameras=db.query(models.Camera_Setting).all()
    
    camera_details=[]
    for camera in cameras:
        cam = camera.__dict__
        camera_out = cam.copy()
        for a in cam:
            if a not in ['camera_number', 'name', 'rtsp', 'room_number']:
                camera_out.pop(a)

        camera_details.append(camera_out)

    return camera_details


@ router.post('/get_camera_image')
def get_camera_image(camera_number: schemas.CameraNumber, current_user: int=Depends(oauth2.get_current_user),
                      db: Session=Depends(get_db)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    camera_details = db.query(models.Camera_Setting).\
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