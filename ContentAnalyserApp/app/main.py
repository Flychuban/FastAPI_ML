from fastapi import FastAPI, Request, Depends

from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import models, crud, database, schemas, utils
from database import SessionLocal
from starlette.concurrency import run_in_threadpool