from fastapi import FastAPI, Request, Depends

from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import models, crud, database, schemas, utils
from database import engine, SessionLocal
from starlette.concurrency import run_in_threadpool

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index2.html", {"request": request})

@app.post("/generate/")
async def generate_content(payload: schemas.GeneratePayload, db: Session = Depends(get_db)):
    generated_text = await run_in_threadpool(utils.generate_content, db, payload.topic)
    return {"generated_text": generated_text}

@app.post("/analyse/")
async def analyse_content(payload: schemas.AnalysePayload, db: Session = Depends(get_db)):
    readability, sentiment = await run_in_threadpool(utils.analyse_content, db, payload.content)
    return {"readability": readability, "sentiment": sentiment}