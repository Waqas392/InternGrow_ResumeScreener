from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time
import uuid
from app.core.config import settings
from app.core.exceptions import InternGrowException
from app.core.logging import logger
from app.db.base import Base
from app.db.session import engine
from app.db.seed import seed_demo_data
from app.api.routes import auth, jobs, resumes, health, evaluation

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    await seed_demo_data()
    yield
    await engine.dispose()

app = FastAPI(title="InternGrow Resume Screening API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    start_time = time.perf_counter()

    response = await call_next(request)

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "request_completed",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2)
        }
    )

    response.headers["X-Request-ID"] = request_id
    return response

@app.exception_handler(InternGrowException)
async def intern_grow_exception_handler(request: Request, exception: InternGrowException):
    return JSONResponse(status_code=exception.status_code, content={"detail": exception.detail})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": jsonable_encoder(exception.errors())}
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exception: Exception):
    logger.error(
        "unhandled_exception",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "path": request.url.path,
            "error": str(exception)
        }
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(resumes.router)
app.include_router(health.router)
app.include_router(evaluation.router)
