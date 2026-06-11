from pydantic import BaseModel,EmailStr
from datetime import datetime
from typing import Optional,Literal


class CreateUser(BaseModel):
    email:EmailStr
    password:str
class SendUserResponse(BaseModel):
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes=True
class PostBase(BaseModel):
    title : str 
    content: str
    published : bool =True
    #rating: Optional[int] =None
class CreatePost(PostBase):
    pass
class SendResponse(PostBase):  #By adding(inherititng) PostBase we don't need to mention the title,contetn,published in this class
   # title :str
    #content: str
    #published : bool =True
    created_at:datetime
    user_id : int
    owner : SendUserResponse
    id : int
    votes: int =0
    class Config:
        from_attributes=True
class UserLogin(BaseModel):
    email:EmailStr
    password:str

    class Config:
        from_attributes=True

class TokenData(BaseModel):
    id : Optional[int] =None

class Token(BaseModel):
    access_token : str
    token_type : str

class Vote(BaseModel):
    post_id:int
    vote_dir:Literal[0,1]
    class Config:
        from_attributes=True




    