from typing import Any, Optional, List, Dict
from fastapi import FastAPI , HTTPException , UploadFile , File , Depends , Header
from pydantic import BaseModel , Field
from contextlib import asynccontextmanager

class Post(BaseModel):
    id : int = Field(ge=1)
    tittle : str
    content : str

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, "posts.json")

def load_posts():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_posts(posts):
    with open(DB_FILE, "w") as f:
        json.dump(posts, f, indent=4)

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading model weights...")
    ml_models["my_model"] = "Loaded Pytorch Model Object"
    yield
    print("Unloading model...")
    ml_models.clear()

app = FastAPI(lifespan = lifespan)

@app.get("/")
def home_page():
    return {"message":"Welcome to Home Page"}

@app.get("/post/{id}")
def get_post(id:int):
    posts_db = load_posts()
    post = [p for p in posts_db if p['id']==id]
    if len(post)!=0:
        return post
    raise HTTPException(status_code=404,detail="Post Not Found")

@app.get("/posts")
def all_posts(id:int = None, tittle:str=None,content:str=None):
    posts_db = load_posts()
    filtered_posts = posts_db
    if id is not None:
        filtered_posts=[p for p in filtered_posts if p["id"]==id]
    if tittle:
        filtered_posts = [p for p in filtered_posts if p["tittle"]==tittle]
    if content:
        filtered_posts = [p for p in filtered_posts if p["content"]==content]
    if len(filtered_posts)!=0:
        return filtered_posts
    return {
        "Message": "All Posts found Without any Filter",
        "Posts":posts_db
            }

@app.post("/post")
def create_post(post:Post):
    posts_db = load_posts()
    for p in posts_db:      
        if p["id"] == post.id:
            raise HTTPException(status_code=400,
                                detail="Posts Already Exists")
    posts_db.append(dict(post))
    save_posts(posts_db)
    return {"Message":"Post Created Successfully", "Post":post}

@app.put("/post")
def update_post(post:Post):
    posts_db = load_posts()
    for p in posts_db:
        if p["id"]== post.id:
            p["tittle"]=post.tittle
            p["content"]= post.content
            save_posts(posts_db)
            return {"Message":"Post updated successfully",
                    "Post":post}
    raise HTTPException(status_code=404, detail="Post does not exist")

@app.delete("/post")
def delete_post(id:int):
    posts_db = load_posts()
    for p in posts_db:
        if p['id']==id:
            posts_db.remove(p)
            save_posts(posts_db)
            return {"Message":"Post deleted successfully",
                    "Post":p}
    raise HTTPException(status_code=404, detail="Post not found")

def varify_api_key(api_key:str = Header(...)):
    if api_key != "token":
        raise HTTPException(status_code = 401,detail = "invalid api key")
    return "Varified Successfully"

@app.post("/predict")
async def predict_image(file: UploadFile = File(...),api_key :str = Depends(varify_api_key)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400,detail="Invalid file type")
    contents = await file.read() 
    file_size = len(contents)
    model = ml_models.get("my_model")
    return {
        "file name":file.filename,
        "model_used": model,
        "file size kb":file_size/1024,
        "prediction": "cat",
        "confidence": 0.97
    }
