
from .import schemas,models
from fastapi import Response, status, HTTPException ,Depends,APIRouter
from sqlalchemy.orm import Session
from .database import  get_db
from typing import List,Optional
from . import oauth2,vote


router=APIRouter(
    prefix="/posts",
    tags=["Posts"]
)




from sqlalchemy import func # ✅ Make sure this is imported at the top!

@router.get("/", response_model=List[schemas.SendResponse])
def get_all_post(db: Session = Depends(get_db), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    
    # 🚀 The Master Query: JOIN and COUNT grouped together
    results = db.query(
        models.Post, 
        func.count(models.Votes.post_id).label("votes") # Calculate total votes and name the column "votes"
    ).join(
        models.Votes, 
        models.Votes.post_id == models.Post.id, 
        isouter=True # This forces a LEFT JOIN so posts with 0 votes still show up!
    ).filter(
        models.Post.title.contains(search)
    ).group_by(
        models.Post.id # Group rows by the Post ID to keep counts accurate
    ).limit(limit).offset(skip).all()

    # ⚠️ CRITICAL STEP: Format the output data stream
    # Because SQLAlchemy returns a list of tuples like [(Post_Object, vote_count)], 
    # we flatten it out so it matches what our response_model expects!
    formatted_posts = []
    for post, vote_count in results:
        post.votes = vote_count
        formatted_posts.append(post)
        
    return formatted_posts

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.SendResponse)
def create_post(payload :schemas.CreatePost, db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    #post_dict=payload.dict()
    #post_dict["id"]=randrange(0,10000)
    #my_posts.append(post_dict)
    #cursor.execute(""" INSERT INTO posts(title,content,published) VALUES(%s,%s,%s) RETURNING * """,
     #              (payload.title,payload.content,payload.published))
    #post=cursor.fetchone()
    #connection.commit()
    #return {"Your newly created post":post}
    #new_post=models.Post(title=payload.title,content=payload.content,published=payload.published)
    print(current_user)
    new_post=models.Post(user_id=current_user.id,**payload.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return  new_post


@router.get("/{id}",response_model=schemas.SendResponse)
def get_one_post(id : int,db: Session=Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    #print("post is is :{id}")
    #cursor.execute("""SELECT * FROM posts WHERE id = %s""",(id,))
    #post=cursor.fetchone()
    post=db.query(models.Post).filter(models.Post.id==id).first()
    if not post:
        raise HTTPException (status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"Post with id {id} was not found")
        #response.status_code = status.HTTP_404_NOT_FOUND
        #return {"message: ": f"Post with id {id} was not found"}
    #if current_user.id != post.user_id:
     #   raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Not authorized to perform requested action")
    total_votes=vote.get_all_likes(id,db)
    post.votes=total_votes
    return post

@router.get("/info/latest",response_model=schemas.SendResponse)
def get_latest_post(db:Session=Depends(get_db)):
    #latest_post=my_posts[len(my_posts)-1]
    #cursor.execute(""" SELECT * FROM posts ORDER BY id DESC LIMIT 1""")
    latest_post=db.query(models.Post).order_by(models.Post.id.desc()).first()
    total_votes=vote.get_all_likes(id,db)
    latest_post.votes=total_votes
    return latest_post


@router.delete("/delete/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id  : int,db:Session=Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    #index=find_index_of_post(id)
   # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""",(id,))
    #deleted_post=cursor.fetchone()
    delete_post=db.query(models.Post).filter(models.Post.id==id)
    if delete_post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} was not found")
    #post=find_post(id)
    if delete_post.first().user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")
    delete_post.delete(synchronize_session=False)
    db.commit()
    #return {"message":f"Following Post has been Deleted: {post}"}
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/update/{id}",response_model=schemas.SendResponse)
def update_post(id:int,post:schemas.PostBase,db:Session =Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    #index=find_index_of_post(id)
    #cursor.execute("""UPDATE posts SET title=%s, content=%s, published=%s WHERE id = %s RETURNING * """, 
     #              (post.title, post.content, post.published, id))
    #updated_post=cursor.fetchone()
    #connection.commit()
    post_query=db.query(models.Post).filter(models.Post.id==id)
    update_post=post_query.first()
    if update_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} doesn't exist")
    #post_dict=post.dict()
    #post_dict["id"]=id
    #my_posts[index]=post_dict
    if update_post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")
    post_query.update(post.dict(),synchronize_session=False)
    db.commit()
    db.refresh(update_post)
    return update_post