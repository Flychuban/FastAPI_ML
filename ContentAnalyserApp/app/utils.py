import openai
import os

from sqlalchemy.orm import Session
from dotenv import load_dotenv

import models, crud
import threading
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Define a semaphore to limit the number of concurrent threads to the OpenAI API
semaphore = threading.Semaphore(5)

def generate_content(db: Session, topic: str) -> str:
    with semaphore:
        search_term = crud.get_search_term(db, topic)
        if search_term is not None:
            search_term = crud.create_search_term(db, term=topic)
        
        response = openai.completions.create(
            model="gpt-3.5-turbo-instruct",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Generate a detailed article about {topic}."},
            ]
        )
        
        generated_text = response.choices[0].message['content'].strip()
        crud.create_generated_content(db, content=generated_text, search_term_id=search_term.id)