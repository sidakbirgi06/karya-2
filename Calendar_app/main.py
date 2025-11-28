# main.py


from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from core import models
from core import database

# --- NEW: Import our routers ---
from Calendar_app.routers import users, events, tasks
from Finance_app.routers import finance
from Notebook_app.routers import notebooks

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


# This is where we "plug in" our "mini-brains"
app.include_router(users.router)
app.include_router(events.router)
app.include_router(tasks.router)
app.include_router(finance.router)
app.include_router(notebooks.router)


# --- Static & Template Setup ---

# 1. Mount the single global static folder
# Note: directory="../static" means "go up one level to find the static folder"
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Templates (Unchanged)
templates = Jinja2Templates(directory="Calendar_app/templates")
templates_finance = Jinja2Templates(directory="Finance_app/templates")
templates_notebook = Jinja2Templates(directory="Notebook_app/templates")

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

@app.get("/finance")
def serve_finance_page(request: Request):
    # We use the NEW "templates_finance" variable here
    return templates_finance.TemplateResponse("finance.html", {"request": request})

@app.get("/finance/summary")
def serve_summary_page(request: Request):
    return templates_finance.TemplateResponse("summary.html", {"request": request})


@app.get("/notebooks")
def serve_notebooks_page(request: Request):
    # This uses the 'templates_notebook' variable we defined earlier
    return templates_notebook.TemplateResponse("notebooks.html", {"request": request})


@app.get("/notebooks/{notebook_id}")
def serve_notebook_canvas(notebook_id: int, request: Request):
    # We pass the 'notebook_id' to the HTML so JavaScript can use it
    return templates_notebook.TemplateResponse("canvas.html", {
        "request": request, 
        "notebook_id": notebook_id
    })