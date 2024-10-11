from fastapi import FastAPI, BackgroundTasks, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import models
from schemas import TranslationRequest, TranslationStatus
from schemas import TaskResponse
import crud
from database import get_db, engine
from sqlalchemy.orm import Session
from utils import perform_translation

# Creating the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/translate", response_model=TaskResponse)
def translate(request: TranslationRequest, background_tasks: BackgroundTasks, get_db: Session = Depends(get_db)):
    task = crud.create_translation_task(request.text, request.languages)
    
    background_tasks.add_task(perform_translation, task.id, request.text, request.languages)
    return {"task_id": task.id}

@app.get(f"/translate/{task_id}", response_model=TranslationStatus)
def translate(request: TranslationRequest, background_tasks: BackgroundTasks, get_db: Session = Depends(get_db)):
    task = crud.create_translation_task(request.text, request.languages)
    
    background_tasks.add_task(perform_translation, task.id, request.text, request.languages)
    return {"task_id": task.id}