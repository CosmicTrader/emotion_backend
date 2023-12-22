from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
import models, schemas, backend_utils, oauth2
from database import get_db
from pydantic import EmailStr
import base64, logging, datetime

router = APIRouter(prefix="/users", tags=['Users'])
blogger = logging.getLogger('backend_logger')

@router.post('/AddOwner', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def owner_registration(user_details: schemas.UserRegistration, db: Session = Depends(get_db)):

    user_email = db.query(models.User).filter(
        models.User.email == user_details.email).first()

    if user_email :
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=(
            f"Email-Id '{user_details.email}' is already registered"))

    if not user_email:
        user_details.is_admin = True
        user_details.is_owner = True
        user_details.password = backend_utils.hash(user_details.password)

        user_details.image = backend_utils.base64_to_image(user_details.image) if user_details.image != '' else None
        new_user = models.User(**user_details.dict())
        new_user.date = datetime.datetime.today().strftime('%Y-%m-%d')

        db.add(new_user)
        db.commit() 
        db.refresh(new_user)
        new_user.owner_id = new_user.id
        db.commit()
        db.refresh(new_user)

        new_user.image = base64.b64encode(new_user.image).decode("utf-8") if new_user.image != None else None
        new_user.date = datetime.datetime.strftime(new_user.date, '%Y-%m-%d')
        return new_user

@router.post('/AddUser', status_code=status.HTTP_201_CREATED)
def user_registration(user_details: schemas.UserRegistration, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    user = db.query(models.User).filter(
        models.User.email == user_details.email).first()
    
    user_details.is_owner = False
    
    if user :

        if user.is_owner == True:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))
        
        existing_user = user_details.__dict__
        if existing_user.get('password'):
            existing_user['password'] = backend_utils.hash(existing_user['password']) if existing_user['password'] != '' else None
        if existing_user.get('image'):
            existing_user['image'] = backend_utils.base64_to_image(existing_user['image']) if existing_user['image'] != '' else None
        
        update_data = {key: value for key, value in existing_user.items() if value != ''}
        try:
            result = db.query(models.User).filter(
                models.User.email == user_details.email).update(update_data)
            db.commit()
            if result:
                return {"message": f"User with email {existing_user['email']} updated successfully"}
        except Exception as e:
            
            if type(e).__name__ == 'IntegrityError':
                return e.__cause__.__dict__['msg']
            
            return False

    if not user :
        new_user = user_details.__dict__
        new_user['password'] = backend_utils.hash(user_details.password)
        if new_user.get('image'):
            new_user['image'] = backend_utils.base64_to_image(user_details.image) if user_details.image != '' else None
            
        new_user = {key: value for key, value in new_user.items() if value != ''}
        new_user = models.User(**new_user)
        new_user.owner_id = current_user.id
        try:
            db.add(new_user)
            db.commit()
            return True 
        except Exception as e:
            
            if type(e).__name__ == 'IntegrityError':
                return e.__cause__.__dict__['msg']
            
            return False

@router.post('/delete_user', status_code=status.HTTP_202_ACCEPTED)
def delete_user(email: schemas.Email, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    user_email = db.query(models.User).filter(
        models.User.email == email.email).first()

    if user_email :
        if user_email.is_owner == True:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
                "Not authorized to perform requested action" ))

        db.delete(user_email)
        db.commit()
        return True
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=(
            f"Requested User details not found"))

@router.get('/user_image')
def get_user_image(email: EmailStr, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=(
            "Not authorized to perform requested action" ))

    user = db.query(models.User).filter_by(email = email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Not authorized to perform requested action')

    if user.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not authorized to perform requested action')
    
    return Response(content=user.image, media_type="image/jpeg")

@router.get('/get_all_user')
def get_all_user(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Not authorized to perform requested action')

    all_users = db.query(models.User).all()

    user_details = []
    for user in all_users:
        _user = user.__dict__
        user_out = _user.copy()
        for a in _user:
            if a not in ['name', 'email', 'mobile_no', 'company', 'is_admin', 'image', 'date']:
                user_out.pop(a)
        user_out['image'] = base64.b64encode(user_out['image']).decode('utf-8') if user_out['image'] != None else ''
        user_details.append(user_out)

    return user_details