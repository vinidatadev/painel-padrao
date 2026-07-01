import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from database import engine, Base
from routes.tasks import router as tasks_router
from routes.auth import router as auth_router
from routes.users import router as users_router

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria tabelas no banco ao iniciar (equivalente ao CREATE TABLE IF NOT EXISTS)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="todo-list-dev API", version="1.0.0", lifespan=lifespan)

# CORS — só aceita requisições das origens configuradas no .env
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok"}
