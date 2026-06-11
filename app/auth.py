from fastapi import FastAPI,Response, status, HTTPException ,Depends,APIRouter
from fastapi.security import  OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .import schemas,models,utils,oauth2
from .database import  get_db



router=APIRouter(tags=["Authentaction"])

     

@router.post("/login",response_model=schemas.Token)
def login(user_credentials:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user=db.query(models.User).filter(models.User.email==user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"Invalid Credentials!")
    if not utils.verify(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"Invalid Credentials!")
    access_token=oauth2.create_access_toekn(data={"user_id":user.id})
    return {"access_token":access_token,"token_type":"bearer"}

