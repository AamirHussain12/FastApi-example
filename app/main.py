from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from .database import get_db,engine
from .import auth, posts
from .import users
from .import vote,models

#commented the below line because this was creating tables in the DB now we atrated using alembic 
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def first_function():
    return {"message":"Hello world!"}

       
    
      

