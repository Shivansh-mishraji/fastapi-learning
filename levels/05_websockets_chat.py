from fastapi import FastAPI , HTTPException , UploadFile , File , Depends , Header , BackgroundTasks , WebSocket , WebSocketDisconnect
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

import time

def heavy_model_inference(filename: str):
    print(f"Background: Starting heavy ML analysis on {filename}...")
    time.sleep(10)
    print(f"Background: ML analysis on {filename} is complete!")

@app.post("/analyze-video")
def analyze_video(filename: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(heavy_model_inference, filename)
    return {"status": "Accepted", "message": f"Processing of '{filename}' has started in the background."}

import asyncio
from fastapi.responses import StreamingResponse , HTMLResponse

async def mock_llm_generator(prompt: str):
    text = f"Replying to: '{prompt}'. Generating tokens one by one... "
    words = text.split()
    for word in words:
        yield word + " "
        await asyncio.sleep(0.3)

@app.get("/stream-llm")
def stream_llm(prompt: str):
    return StreamingResponse(mock_llm_generator(prompt), media_type="text/event-stream")

from fastapi import WebSocket , WebSocketDisconnect
from fastapi.responses import HTMLResponse

html_code = """
<!DOCTYPE html>
<html>
    <head><title>AI Chat</title></head>
    <body>
        <h2>Real-time AI Chat</h2>
        <input type="text" id="messageText" autocomplete="off"/>
        <button onclick="sendMessage()">Send</button>
        <ul id='messages'></ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages');
                var message = document.createElement('li');
                var content = document.createTextNode(event.data);
                message.appendChild(content);
                messages.appendChild(message);
            };
            function sendMessage() {
                var input = document.getElementById("messageText");
                ws.send(input.value);
                input.value = '';
            }
        </script>
    </body>
</html>
"""

@app.get("/chat-room")
def get_chat_room():
    return HTMLResponse(html_code)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"AI ASSISTANT: You Said '{data}'")
    except WebSocketDisconnect:
        print("Client disconnected")
