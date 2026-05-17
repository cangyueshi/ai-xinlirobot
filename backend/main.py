from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base, SessionLocal
from models import user, appointment, chat, assessment
from routers import auth, appointments, chat as chat_router, assessments, counselor
from utils.seed_scales import seed_scales

Base.metadata.create_all(bind=engine)

db = SessionLocal()
seed_scales(db)
db.close()

app = FastAPI(title="AI 心理咨询机器人 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(appointments.router)
app.include_router(chat_router.router)
app.include_router(assessments.router)
app.include_router(counselor.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "AI 心理咨询机器人服务运行中"}