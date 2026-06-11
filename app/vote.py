from fastapi import status, HTTPException ,Depends,APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from . database import  get_db
from . import oauth2,schemas,models



router=APIRouter(
    prefix="/vote",
    tags=["VOTES"]
)

def get_all_likes(post_id,db:Session):
   total_votes= db.query(func.count(models.Votes.post_id)).filter(models.Votes.post_id==post_id).scalar()
   return total_votes if total_votes is not None else 0
    
@router.post("/",status_code=status.HTTP_201_CREATED)
def vote(vote:schemas.Vote,db:Session=Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    post=db.query(models.Post).filter(models.Post.id==vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Post with id : {vote.post_id} does not exist")
    vote_query=db.query(models.Votes).filter(models.Votes.post_id==vote.post_id,
                                             models.Votes.user_id==current_user.id)
    found_vote=vote_query.first()
    if (vote.vote_dir==1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"User {current_user.id} has already voted on post {vote.post_id}")
        new_vote=models.Votes(user_id=current_user.id,post_id=vote.post_id)
        db.add(new_vote)
        db.commit()
        return {"message":"Sucessfully added a vote!"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Vote does not exist")
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Vote sucessfully Deleted"}

        
    