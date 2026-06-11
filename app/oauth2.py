import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import  status, HTTPException ,Depends
from .import models
from .database import get_db
from sqlalchemy.orm import Session
from datetime import datetime,timedelta
from .import schemas
from .config import settings


SECRET_KEY=settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
Oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")

def create_access_toekn(data:dict):
    to_encode=data.copy()
    expire_time=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire_time})
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def verify_acess_token(token : str,credentials_exceptions):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        id : str = payload.get("user_id")

        if id is None:
            raise credentials_exceptions
        token_data= schemas.TokenData(id=id)
    except jwt.InvalidTokenError:
        raise credentials_exceptions
    return token_data
    
def get_current_user(token:str=Depends(Oauth2_scheme),db:Session=Depends(get_db)):
    credentials_exceptions=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"Could not validate credentials",
                                        headers={"WWW-Authenticate":"Bearer"})
    token= verify_acess_token(token,credentials_exceptions)
    user= db.query(models.User).filter(models.User.id==token.id).first()
    return user