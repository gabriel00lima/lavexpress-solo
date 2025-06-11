# ===== app/main.py =====
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, user, car_wash, service, booking, review
from app.database import engine
from app.models import user as user_models
from app.models import car_wash as car_wash_models
from app.models import service as service_models
from app.models import booking as booking_models
from app.models import review as review_models

# Criar tabelas
user_models.Base.metadata.create_all(bind=engine)
car_wash_models.Base.metadata.create_all(bind=engine)
service_models.Base.metadata.create_all(bind=engine)
booking_models.Base.metadata.create_all(bind=engine)
review_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CarWash API",
    description="API para agendamento de lava-jatos",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(car_wash.router, prefix="/car-wash", tags=["car-wash"])
app.include_router(service.router, prefix="/service", tags=["service"])
app.include_router(booking.router, prefix="/booking", tags=["booking"])
app.include_router(review.router, prefix="/review", tags=["review"])

@app.get("/")
async def root():
    return {"message": "CarWash API v1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# ===== app/database.py =====
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

DATABASE_URL = config('DATABASE_URL')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()