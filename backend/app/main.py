from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import get_settings
from app.routers import auth, profile, content, challenges, ai, subscriptions, affiliates, admin

settings = get_settings()

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="מועדון הספורטאים API",
    description="פלטפורמה דיגיטלית לליווי ספורטאים צעירים בישראל",
    version="1.0.0",
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url=None,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(content.router)
app.include_router(challenges.router)
app.include_router(ai.router)
app.include_router(subscriptions.router)
app.include_router(affiliates.router)
app.include_router(admin.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "moadon-hasportaim"}
