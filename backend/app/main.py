from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.database import engine, Base, SessionLocal, init_db_data
from app.routers import auth, applications, stats
import app.models  # 注册 SQLAlchemy 模型到 Base.metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        init_db_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="丰收节临时摊位用电申报系统",
    description="乡镇丰收节筹备组临时摊位用电申报管理系统",
    version="1.0.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(applications.router, prefix="/api/applications", tags=["用电申报"])
app.include_router(stats.router, prefix="/api/stats", tags=["统计导出"])


@app.get("/")
def root():
    return {"message": "丰收节临时摊位用电申报系统 API 服务运行中"}
