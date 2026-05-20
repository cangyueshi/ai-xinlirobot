import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import engine, Base, SessionLocal
from models import user, appointment, chat, assessment
from routers import auth, appointments, chat as chat_router, assessments, counselor, admin
from utils.seed_scales import seed_scales
from utils.seed_admin import seed_super_admin
from utils.seed_test_data import seed_test_counselor
from config import settings

Base.metadata.create_all(bind=engine)

# 为已有数据库添加新列（counselor_summary）
from sqlalchemy import text as sa_text
try:
    with engine.connect() as conn:
        conn.execute(sa_text("ALTER TABLE chat_sessions ADD COLUMN counselor_summary TEXT"))
        conn.commit()
except Exception:
    pass  # 列已存在则忽略

db = SessionLocal()
seed_scales(db)
seed_super_admin(db)
seed_test_counselor()
db.close()

app = FastAPI(title="AI 心理咨询机器人 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(appointments.router)
app.include_router(chat_router.router)
app.include_router(assessments.router)
app.include_router(counselor.router)
app.include_router(admin.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "AI 心理咨询机器人服务运行中"}


# ==================== 托管前端 H5 静态文件（生产/测试模式） ====================

FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist", "build", "h5")

if os.path.isdir(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # API 路径已经由 router 处理，这里只兜底返回前端页面
        if full_path.startswith("api/"):
            from fastapi.responses import JSONResponse
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        # index.html 禁止缓存，确保浏览器每次获取最新版本
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"), headers={"Cache-Control": "no-cache, no-store, must-revalidate"})