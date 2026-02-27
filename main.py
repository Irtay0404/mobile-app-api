from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from database import close_pool
from routers import recognize, checkout


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_pool()


app = FastAPI(title="Cashierless API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для демо; в проде ограничить
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recognize.router)
app.include_router(checkout.router)


@app.get("/health")
async def health():
    return {"status": "ok"}