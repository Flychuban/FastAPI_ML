from pydub import AudioSegment
import logging
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import os
import requests
import speech_recognition as sr
import openai

def convert_mp3_to_wav(mp3_file_path, wav_file_path):
    # Convert mp3 to wav
    sound = AudioSegment.from_mp3(mp3_file_path)
    sound.export(wav_file_path, format="wav")
    logging.info(f"Converted {mp3_file_path} to {wav_file_path}")

def split_audio(wav_path, chunk_length_ms=60000):
    audio = AudioSegment.from_wav(wav_path)
    chunks = [audio[i:i+chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
    return chunks

def transcribe_audio_chunk(chunk, chunk_index):
    chunk_path = f"chunk_{chunk_index}.wav"
    chunk.export(chunk_path, format="wav")
    
    try:
        with open(chunk_path, "rb") as audio_file:
            response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
            text = response['text']
    except Exception as e:
        logging.error(f"Error transcribing chunk {chunk_index}: {e}")
        text = ""
    finally:
        os.remove(chunk_path)
    return text        
    