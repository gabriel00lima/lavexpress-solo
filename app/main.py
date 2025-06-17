# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação"""
    # Startup
    logger.info("🚀 Iniciando CarWash API...")

    try:
        # Importações só quando necessário (evita problemas circulares)
        from app.database import test_connection, create_tables

        # Testa conexão com banco
        logger.info("🔍 Testando conexão com banco de dados...")
        if test_connection():
            logger.info("✅ Conexão com banco OK!")

            # Cria tabelas se necessário
            logger.info("📋 Criando/verificando tabelas...")
            create_tables()
            logger.info("✅ Tabelas verificadas!")

        else:
            logger.warning("⚠️  Banco de dados não disponível!")
            logger.warning("🔧 A API vai iniciar, mas funcionalidades de banco não estarão disponíveis")
            logger.warning("💡 Verifique se o PostgreSQL está rodando")

    except Exception as e:
        logger.error(f"❌ Erro na inicialização do banco: {e}")
        logger.warning("⚠️  A API vai iniciar sem banco de dados")

    logger.info("🎉 CarWash API iniciada com sucesso!")

    yield  # Aplicação rodando

    # Shutdown
    logger.info("🛑 Finalizando CarWash API...")


# Criar aplicação FastAPI
app = FastAPI(
    title="CarWash API",
    description="API para agendamento de lava-jatos",
    version="1.0.0",
    lifespan=lifespan  # Usa gerenciador de ciclo de vida
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar e incluir rotas
try:
    from app.routes import auth, user, car_wash, service, booking, review

    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(user.router, prefix="/user", tags=["user"])
    app.include_router(car_wash.router, prefix="/car-wash", tags=["car-wash"])
    app.include_router(service.router, prefix="/service", tags=["service"])
    app.include_router(booking.router, prefix="/booking", tags=["booking"])
    app.include_router(review.router, prefix="/review", tags=["review"])

    logger.info("✅ Todas as rotas carregadas com sucesso!")

except Exception as e:
    logger.error(f"❌ Erro ao carregar rotas: {e}")
    logger.warning("⚠️  Algumas rotas podem não estar disponíveis")


# Rotas básicas
@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "CarWash API v1.0.0",
        "status": "online",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Verifica saúde da API"""
    try:
        from app.database import test_connection
        db_status = "connected" if test_connection() else "disconnected"
    except Exception:
        db_status = "error"

    return {
        "status": "healthy",
        "api": "online",
        "database": db_status,
        "version": "1.0.0"
    }


@app.get("/info")
async def get_info():
    """Informações da API"""
    return {
        "name": "CarWash API",
        "version": "1.0.0",
        "description": "API para agendamento de lava-jatos",
        "endpoints": {
            "auth": "/auth/*",
            "users": "/user/*",
            "car_washes": "/car-wash/*",
            "services": "/service/*",
            "bookings": "/booking/*",
            "reviews": "/review/*"
        },
        "documentation": "/docs"
    }


# Para desenvolvimento local
if __name__ == "__main__":
    import uvicorn

    logger.info("🔧 Modo desenvolvimento - iniciando servidor...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )