from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from schemas import LyricsPayload
from utils import summarize_text, transcribe_audio_chunk, transcribe_wav_to_text, convert_mp3_to_wav, split_audio

import os
from io import BytesIO
from pydub import AudioSegment
from PIL import Image
from dotenv import load_dotenv
import logging
import speech_recognition as sr
import openai
import requests

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

logging.basicConfig(level=logging.INFO)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("converted_files"):
    os.makedirs("converted_files")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return templates.TemplateResponse("index.html", {"request": {}})


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...), language: str = Form(...)):
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
        
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
        
    # Audio processing
    wav_file_location = f"converted_files/{file.filename.replace('.mp3', '.wav')}"
    convert_mp3_to_wav(file_location, wav_file_location)
    
    lyrics = transcribe_wav_to_text(wav_file_location)
    os.remove(file_location)
    
    summary = await summarize_text(lyrics)
    return {"lyrics": lyrics, "summary": summary}
    