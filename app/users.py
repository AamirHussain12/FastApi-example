
from . import schemas,models,utils
from fastapi import  status, HTTPException , Depends,APIRouter
from sqlalchemy.orm import Session
from . database import get_db

router=APIRouter(
    prefix="/user",
    tags=["Users"]
)

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.SendUserResponse)
def create_user(data : schemas.CreateUser,db:Session=Depends(get_db)):
    try:
        data.password=utils.hash(data.password)
        user=models.User(**data.dict())
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as error:
        db.rollback()
        if "email" in str(error.orig):
            error_msg="Signup failed! Data Error: Email already exists"
        else:
            error_msg = "User signup failed! Data Error: unique constraint violation."
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=error_msg)
    
@router.get("/{id}",response_model=schemas.SendUserResponse)
def get_user(id:int,db:Session=Depends(get_db)):
    user=db.query(models.User).filter(models.User.id==id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"User not found!")
    return user

