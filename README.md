# 🚀 FastAPI Deep Dive — AI/ML Engineering Practice

A comprehensive, hands-on FastAPI practice repository covering all production-level concepts required for **AI/ML Engineer** roles. Every concept is implemented with real code, honest documentation of mistakes made, and the reasoning behind each pattern.

---

## 📌 What This Repository Is

This is not a tutorial copy-paste. This is a **learning journal in code** — built by actually writing, breaking, fixing, and understanding every single pattern from scratch. Every mistake made is documented here as a learning resource for anyone following the same path.

---

## 🗂️ File Structure

```text
FastAPi/
│
├── practice.py                 ← Main file: All 10 FastAPI concepts implemented
├── levels/                     ← Step-by-step level implementations
│   ├── 01_crud_basics.py       ← Level 1-3: Routing, Pydantic, CRUD
│   ├── 02_image_upload_auth.py ← Level 4-5: File upload, Auth, Lifespan loading
│   ├── 03_background_tasks.py  ← Level 7: Non-blocking Background Tasks
│   ├── 04_llm_streaming.py     ← Level 8: Streaming responses (SSE)
│   └── 05_websockets_chat.py   ← Level 9: Real-time WebSockets chat
└── README.md                   ← This file
```

You can view the individual step-by-step files in the [levels/](file:///c:/Users/91727/Desktop/FastAPi/levels) directory, with [practice.py](file:///c:/Users/91727/Desktop/FastAPi/practice.py) containing the complete unified project code.

---

## 📚 What I Covered (10 Levels)

| Level | Topic | Key Concept |
|-------|-------|-------------|
| 1 | Basic Routing & Path Parameters | `@app.get`, path params, query params |
| 2 | Pydantic Models & Input Validation | `BaseModel`, `Field(ge=1)` constraints |
| 3 | Full CRUD Operations | GET, POST, PUT, DELETE with proper HTTP codes |
| 4 | Async File Uploads | `UploadFile`, `await file.read()` |
| 5 | Dependency Injection & API Key Auth | `Depends`, `Header`, protected routes |
| 6 | Lifespan Context Manager | Startup/shutdown model loading for AI |
| 7 | Background Tasks | Non-blocking heavy ML inference |
| 8 | Streaming Responses (SSE) | Token-by-token LLM output streaming |
| 9 | WebSockets | Real-time bidirectional chat |
| 10 | Middleware | Global latency tracking & request logging |

---

## 🐛 Mistakes I Made & What I Learned

This is the most important section. Real learning happens through mistakes.

### 1. Pydantic Model vs Dictionary — `TypeError`
**What I wrote:**
```python
if post["id"] in posts_db:  # ❌ Wrong — post is a Pydantic model, not a dict
```
**What crashed:** `TypeError: 'Post' object is not subscriptable`

**The fix:**
```python
if post.id == p["id"]:  # ✅ Correct — use dot notation on Pydantic models
```
**Lesson:** Pydantic models are Python **objects**. Access their fields with `.attribute`, not `["key"]`.

---

### 2. Mixed Types in the Database List — `TypeError` on GET
**What I wrote:**
```python
posts_db.append(post)  # ❌ Appending a Pydantic object into a list of dicts
```
**What crashed:** When GET routes tried `p["id"]` on the Pydantic object, it crashed.

**The fix:**
```python
posts_db.append(dict(post))  # ✅ Convert to dict first
```
**Lesson:** Never mix types inside a list. Keep your data store consistent.

---

### 3. Wrong Filter Logic — Overwrites Previous Filter
**What I wrote:**
```python
if id: filtered_posts = [p for p in posts_db ...]    # Filters posts_db
if tittle: filtered_posts = [p for p in posts_db ...]  # ❌ Overwrites! Uses posts_db again
```
**The fix:**
```python
if tittle: filtered_posts = [p for p in filtered_posts ...]  # ✅ Chains correctly
```
**Lesson:** When chaining filters, always filter the already-filtered list.

---

### 4. String Slicing Bug — Wrong Character Count
**What I wrote:**
```python
if file.content_type[0:5] == "image/":  # ❌ Slices 5 chars, but "image/" is 6 chars!
```
**Result:** "image/jpeg" → slice gives "image" (no slash) → never equals "image/" → 400 error.

**The fix:**
```python
if file.content_type.startswith("image/"):  # ✅ Clean and safe
```
**Lesson:** Never manually slice strings for prefix checks. Use `.startswith()`.

---

### 5. `.startswith` Without Parentheses
**What I wrote:**
```python
if file.content_type.startswith == "image/":  # ❌ Comparing the method itself, not calling it
```
**The fix:**
```python
if file.content_type.startswith("image/"):  # ✅ Call it with ()
```
**Lesson:** In Python, methods need `()` to be **called**. Without `()`, you get the function object itself.

---

### 6. `return` Instead of `raise` for HTTPException
**What I wrote:**
```python
return HTTPException(status_code=400, detail="Invalid")  # ❌ Returns a 200 OK!
```
**The fix:**
```python
raise HTTPException(status_code=400, detail="Invalid")  # ✅ Triggers the actual error
```
**Lesson:** `HTTPException` must be **raised**, not returned. Returning it just sends the object as a normal 200 OK response.

---

### 7. WebSocket Closes After One Message — Missing `while True`
**What I wrote:**
```python
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_text()   # ❌ Only receives ONE message
    await websocket.send_text(f"You said: {data}")
    # Function ends → connection closes!
```
**The fix:**
```python
while True:
    data = await websocket.receive_text()
    await websocket.send_text(f"You said: {data}")
```
**Lesson:** Without `while True`, the WebSocket function exits after the first message, closing the connection.

---

### 8. `yield` Outside the Lifespan Function — `SyntaxError`
**What I wrote:**
```python
async def lifespan(app):
    ml_models["model"] = "loaded"

yield  # ❌ Not indented! Outside the function body.
```
**The fix:**
```python
async def lifespan(app):
    ml_models["model"] = "loaded"
    yield  # ✅ Indented inside the function
    ml_models.clear()
```
**Lesson:** Indentation is everything in Python. The `yield` and shutdown code must be inside the function.

---

## ⚡ API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|:---:|
| `GET` | `/` | Home page | ❌ |
| `GET` | `/posts` | Get all posts (filterable) | ❌ |
| `GET` | `/post/{id}` | Get a single post by ID | ❌ |
| `POST` | `/post` | Create a new post | ❌ |
| `PUT` | `/post` | Update an existing post | ❌ |
| `DELETE` | `/post` | Delete a post by ID | ❌ |
| `POST` | `/predict` | AI image classification | ✅ `api-key: token` |
| `POST` | `/analyze-video` | Trigger background ML task | ❌ |
| `GET` | `/stream-llm` | Stream LLM response (SSE) | ❌ |
| `GET` | `/chat-room` | Open WebSocket chat UI | ❌ |
| `WS` | `/ws` | Real-time WebSocket endpoint | ❌ |

---

## 🚀 Running the App

```bash
# Install dependencies
pip install fastapi uvicorn python-multipart

# Run the development server
uvicorn practice:app --reload
```

Open Swagger UI: **http://127.0.0.1:8000/docs**

### Testing Streaming:
```bash
curl.exe -N "http://127.0.0.1:8000/stream-llm?prompt=hello"
```

### Testing WebSocket Chat:
Open **http://127.0.0.1:8000/chat-room** in your browser.

---

## 🧠 Key Concepts Understood

- **`def` vs `async def`**: CPU-heavy tasks (local model inference) should use regular `def` — FastAPI runs them in a thread pool. I/O-bound tasks (calling external APIs, reading files) should use `async def`.
- **Why Lifespan?**: Loading a model inside each request function reloads it from disk on EVERY request. Lifespan loads it ONCE into RAM and keeps it there.
- **Why Streaming?**: Without streaming, users stare at a loading spinner for 10-30 seconds waiting for a full LLM response. Streaming sends tokens the moment they are generated.
- **Why WebSockets over HTTP for chat?**: HTTP requires a new connection for every message. WebSockets keep a single open tunnel, enabling real-time, instant communication.
- **Why Middleware?**: To measure performance, log requests, or add headers globally without repeating code in every single route.

---

## 🛣️ What's Next

- [ ] Connect to a real SQL database using SQLAlchemy / SQLModel
- [ ] Integrate HuggingFace Transformers for real model inference
- [ ] Build a full RAG (Retrieval-Augmented Generation) API
- [ ] Dockerize the application
- [ ] Deploy to cloud (Render / Railway / GCP Cloud Run)

---

## 🤖 How I Learned This (AI-Augmented Learning)

This project was built using what I consider the most effective learning method for 2024 and beyond: **learning by building, with an AI as your senior mentor**.

Here is exactly how the process worked:

**I wrote the code. The AI reviewed it.**
Every route, every model, every function was written by me first. I then asked the AI to review my code, point out what was wrong, and — most importantly — explain *why* it was wrong. The goal was never to get the right answer. The goal was to understand the reason behind the answer.

**Real debugging sessions.**
Many of the mistakes documented in this README were real bugs I hit during this process. When my WebSocket only responded once, I didn't just ask "what's wrong". I asked "why does this function exit after one message, and what does that tell me about how Python function lifecycles work?" That kind of questioning led to a much deeper understanding than any tutorial could give.

**Concept → Question → Code → Break → Fix → Understand.**
That was the loop. Not: Watch video → Copy code → Move on.

**Why this approach matters:**
Senior engineers at top companies use AI tools to write faster, debug smarter, and research architectural decisions in real time. Learning *how* to collaborate with AI effectively — asking the right questions, critically reviewing its output, and building your own mental model — is itself a high-demand engineering skill.

This repository is proof of that process: a working, production-aware FastAPI codebase with honest documentation of every mistake made along the way.

---

## 🙏 Acknowledgements

Built with purpose, debugged with patience, and documented with honesty.
If you are on the same journey — building toward a career in AI/ML Engineering — feel free to connect. Every documented mistake in this repo was a real learning moment, and I hope it helps someone else skip the confusion and get to the understanding faster.
