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

@app.post("/generate_image/")
async def generate_image(payload: LyricsPayload):
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logging.error("OpenAI API Key not found")
            raise HTTPException(status_code=500, detail="OpenAI API Key not found")
        openai.api_key = api_key
        
        dalle_url = "https://api.openai.com/v1/images/generations"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        prompt = f"Create an image of the following lyrics: {payload.lyrics}"
        
        if len(prompt) > 1000:
            prompt = prompt[:1000]
        
        data = {
            "size": "1024x1024",
            "prompt": prompt,
            "n": 1
        }
        logging.info(f"Sending request to OpenAI DALL-E: {data}")
        response = requests.post(dalle_url, json=data, headers=headers)
        logging.info(f"Received response from OpenAI DALL-E: {response.json()}")
        
        image_url = response.json()['data'][0]['url']
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        
        image = Image.open(BytesIO(image_response.content))
        if not os.path.exists("media"):
            os.makedirs("media")
        image_path = os.path.join("media", "generated_image.jpg")
        image.save(image_path)
        logging.info(f"Saved image to {image_path}")
        return {"image_path": image_path}
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error generating image: {e}")
        raise HTTPException(status_code=500, detail="Error generating image")

@app.get("/media/generated_image.png")
async def get_generated_image():
    return FileResponse("media/generated_image.jpg")