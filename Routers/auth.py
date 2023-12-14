from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import database, schemas, models, backend_utils, oauth2
import base64, logging

router = APIRouter(prefix="", tags=['Authentication'])
blogger = logging.getLogger('backend_logger')

@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):

    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User Does not exist.")

    if not backend_utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    oauth2.invalidate_old_token(user.id)
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    image = base64.b64encode(user.image).decode("utf-8") if user.image != None else ''
    
    return {"access_token": access_token, "token_type": "bearer", "username": user.name, "image": image, 'is_owner': user.is_owner, 'is_admin' : user.is_admin}
