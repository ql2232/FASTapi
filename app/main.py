from fastapi import FastAPI, Response, HTTPException, status, Depends
from fastapi.params import Body

from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models, schemas
from sqlalchemy.orm import Session
from .database import engine, get_db, SessionLocal
from passlib.context import CryptContext

models.Base.metadata.create_all(bind=engine)

app = FastAPI()



@app.get("/sqlalchemy")                                         #same as dependency, but more coding
def test_db():
    db = SessionLocal()
    try:
        currPosts = db.query(models.Post).all()
    finally:
        db.close()
    return {"data": currPosts}



while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastAPI', user='postgres',
                                password='Yeetung@20100726', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful!")
        break
    except Exception as error:
        print("Connection Failed")
        time.sleep(2)



@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model= schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # newPost = models.Post(**post.dict())
    newPost = models.Post(title=post.title, content=post.content, published=post.published)
    db.add(newPost)
    db.commit()
    db.refresh(newPost)

    return newPost


@app.get("/")                               #turns it to a route
def root():
    return {"message": "Welcome"}                   #FASTapi will convert it to JSON, use JSON to send data back and forth

@app.get("/posts")                               #turns it to a route
def posts(db: Session = Depends(get_db)):
    currPosts = db.query(models.Post).all()
    return currPosts


@app.get("/posts/{id}", response_model=schemas.PostResponse)                               #turns it to a route
def get_post(id: int, db: Session = Depends(get_db)):
    currPost = db.query(models.Post).filter(models.Post.id == id).first()
    if not currPost:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return currPost.__dict__



@app.delete("/posts/{currId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(currId: int, db: Session = Depends(get_db)):
    postQuery = db.query(models.Post).filter(models.Post.id == currId)

    if postQuery.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {currId} does not exist")

    postQuery.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)




@app.put("/posts/{currId}", response_model=schemas.PostResponse)
def update_post(currId: int, currPost: schemas.PostCreate, db: Session = Depends(get_db) ):
    postQuery = db.query(models.Post).filter(models.Post.id == currId)
    if postQuery.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {currId} does not exist")
    postQuery.update(currPost.dict(), synchronize_session=False)

    db.commit()
    return postQuery.first()


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_users(user: schemas.UserBase, db: Session = Depends(get_db)):
    newUser = models.User(**user.dict())

    currUser = db.query(models.User).filter(models.User.email == user.email)
    if currUser.first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"post with mail: {user.email} already exists")

    db.add(newUser)
    db.commit()
    db.refresh(newUser)
    return newUser
