from datetime import datetime, timedelta
from jose import jwt, JWTError
import json

from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import schemas, database, models


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/login')

SECRET_KEY = 'lhsdoohigjdmhfdloiEOFFlkhflakhhfOHGGLLDFFLJJKKANNFFHDFFHEFF'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 300

active_tokens = {}

def create_access_token(data: dict):

    global active_tokens

    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    user_id = data.get("user_id")
    if user_id:
        active_tokens[user_id] = encoded_jwt
        with open('active_tokens.json', 'w') as tokens:
            tokens.write(json.dumps(active_tokens))

    return encoded_jwt

def invalidate_old_token(user_id: str):
    global active_tokens

    old_token = active_tokens.get(user_id)
    if old_token :
        active_tokens.pop(user_id)
        with open('active_tokens.json', 'w') as tokens:
            tokens.write(json.dumps(active_tokens))

    return

def verify_access_token(token: str, credentials_exception):
    global active_tokens

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        
        if id is None:
            raise credentials_exception
        
        if active_tokens[id] != token:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)

    except JWTError:
        if active_tokens[id] != token:
            raise credentials_exception

        token_data = schemas.TokenData(id=id)
        return token_data

    except Exception as e :
        raise credentials_exception
    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    global active_tokens
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user