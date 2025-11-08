# main.py

from dotenv import load_dotenv  # <-- ADD THIS
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import models
import database

# --- NEW: Import our routers ---
from routers import users, events, tasks

# --- Database & App Setup ---
# This line creates our tables (app.db) if they don't exist
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# --- CORS Middleware (Unchanged) ---
# This allows our frontend to talk to our backend
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "null"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- NEW: Include the Routers ---
# This is where we "plug in" our "mini-brains"
app.include_router(users.router)
app.include_router(events.router)
app.include_router(tasks.router)


# --- Static & Template Setup (Unchanged) ---
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# --- Page Serving Endpoints (Unchanged) ---
# These are the only endpoints left in main.py

@app.get("/signup")
def serve_signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/login")
def serve_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/")
def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})