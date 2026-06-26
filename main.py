from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import engine
from router import auth, section
 
from schemas import *

@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    #shutdown
    await engine.dispose()

# initialize FastAPI app 
app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(auth.router, prefix="/account")
app.include_router(section.router, prefix="/section")