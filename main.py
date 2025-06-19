#!/usr/bin/env python3
"""
CarWash API - Sistema de Agendamento de Lava-Jatos
FastAPI application with complete router management and error handling
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import traceback
import sys
import os
import time

# Configurar logging detalhado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('carwash_api.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Adicionar diretório atual ao Python path se necessário
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação"""
    # ========================
    # STARTUP
    # ========================
    logger.info("🚀 Iniciando CarWash API...")
    logger.info(f"📍 Diretório atual: {os.getcwd()}")
    logger.info(f"🐍 Python Path: {sys.path[:3]}...")  # Primeiros 3 caminhos

    # Verificar estrutura de arquivos
    logger.info("📂 Verificando estrutura de arquivos...")
    app_dir = os.path.join(current_dir, 'app')
    routes_dir = os.path.join(app_dir, 'routes')

    if os.path.exists(app_dir):
        logger.info(f"✅ Pasta 'app' encontrada: {app_dir}")

        if os.path.exists(routes_dir):
            logger.info(f"✅ Pasta 'routes' encontrada: {routes_dir}")

            # Listar arquivos de rotas
            try:
                route_files = [f for f in os.listdir(routes_dir) if f.endswith('.py')]
                logger.info(f"📄 Arquivos de rotas encontrados: {route_files}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao listar arquivos de rotas: {e}")
        else:
            logger.error(f"❌ Pasta 'routes' não encontrada em: {routes_dir}")
    else:
        logger.error(f"❌ Pasta 'app' não encontrada em: {app_dir}")

    # Inicialização do banco de dados
    try:
        logger.info("🔍 Testando conexão com banco de dados...")
        from app.database import test_connection, create_tables

        if test_connection():
            logger.info("✅ Conexão com banco OK!")

            # Cria tabelas se necessário
            logger.info("📋 Criando/verificando tabelas...")
            create_tables()
            logger.info("✅ Tabelas verificadas!")

        else:
            logger.warning("⚠️ Banco de dados não disponível!")
            logger.warning("🔧 A API vai iniciar, mas funcionalidades de banco não estarão disponíveis")
            logger.warning("💡 Verifique se o PostgreSQL está rodando")

    except ImportError as e:
        logger.error(f"❌ Erro de importação do módulo database: {e}")
        logger.warning("⚠️ Módulo database não encontrado - verifique se app/database.py existe")
    except Exception as e:
        logger.error(f"❌ Erro na inicialização do banco: {e}")
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")
        logger.warning("⚠️ A API vai iniciar sem banco de dados")

    logger.info("🎉 CarWash API iniciada com sucesso!")

    yield  # ← Aplicação rodando aqui

    # ========================
    # SHUTDOWN
    # ========================
    logger.info("🛑 Finalizando CarWash API...")


# ========================
# CRIAR APLICAÇÃO FASTAPI
# ========================
app = FastAPI(
    title="CarWash API",
    description="API para agendamento de lava-jatos",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ========================
# MIDDLEWARE
# ========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:19006",  # ← ADICIONAR ESTA LINHA
        "http://127.0.0.1:19006",
        "http://192.168.0.94:19006",  # Adicione se ainda não tiver
        "exp://192.168.0.94:19006",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "*"  # Permitir todos para desenvolvimento
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request, call_next):
    """Log todas as requisições"""
    start_time = time.time()

    # Log da requisição
    logger.info(f"📥 {request.method} {request.url}")

    # Processar requisição
    response = await call_next(request)

    # Log da resposta
    process_time = time.time() - start_time
    logger.info(f"📤 {request.method} {request.url} - {response.status_code} ({process_time:.3f}s)")

    return response


# ========================
# IMPORTAR E INCLUIR ROTAS
# ========================
def load_routers():
    """Carrega todos os routers de forma segura"""
    routers_loaded = []
    routers_failed = []

    # Lista de routers para carregar
    router_configs = [
        {"module": "auth", "prefix": "/auth", "tags": ["auth"]},
        {"module": "user", "prefix": "/user", "tags": ["user"]},
        {"module": "car_wash", "prefix": "/car-wash", "tags": ["car-wash"]},
        {"module": "service", "prefix": "/service", "tags": ["service"]},
        {"module": "booking", "prefix": "/booking", "tags": ["booking"]},
        {"module": "review", "prefix": "/review", "tags": ["review"]},
    ]

    for config in router_configs:
        try:
            # Importação dinâmica
            module_name = f"app.routes.{config['module']}"
            logger.info(f"🔄 Carregando router: {module_name}")

            # Importar o módulo
            module = __import__(module_name, fromlist=[config['module']])

            # Verificar se tem o atributo router
            if hasattr(module, 'router'):
                app.include_router(
                    module.router,
                    prefix=config['prefix'],
                    tags=config['tags']
                )
                routers_loaded.append(config['module'])
                logger.info(f"✅ Router '{config['module']}' carregado com sucesso!")
            else:
                routers_failed.append(f"{config['module']} (sem atributo 'router')")
                logger.error(f"❌ Router '{config['module']}' não tem atributo 'router'")

        except ImportError as e:
            routers_failed.append(f"{config['module']} (ImportError: {str(e)})")
            logger.error(f"❌ Erro ao importar router '{config['module']}': {e}")

        except Exception as e:
            routers_failed.append(f"{config['module']} (Erro: {str(e)})")
            logger.error(f"❌ Erro inesperado ao carregar router '{config['module']}': {e}")
            logger.error(f"🔍 Traceback: {traceback.format_exc()}")

    # Relatório final
    if routers_loaded:
        logger.info(f"✅ Routers carregados com sucesso: {', '.join(routers_loaded)}")

    if routers_failed:
        logger.warning(f"⚠️ Routers com problemas: {', '.join(routers_failed)}")

    return routers_loaded, routers_failed


# Carregar routers
loaded_routers, failed_routers = load_routers()


# ========================
# ROTAS BÁSICAS E SISTEMA
# ========================

@app.get("/", summary="Root", description="Endpoint raiz da API")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "CarWash API v1.0.0",
        "status": "online",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "info": "/info",
        "routers_loaded": len(loaded_routers),
        "routers_failed": len(failed_routers)
    }


@app.get("/health", summary="Health Check", description="Verifica saúde da API")
async def health_check():
    """Verifica saúde da API"""
    health_data = {
        "status": "healthy",
        "api": "online",
        "version": "1.0.0",
        "routers": {
            "loaded": loaded_routers,
            "failed": failed_routers,
            "total_loaded": len(loaded_routers),
            "total_failed": len(failed_routers)
        }
    }

    # Testar conexão com banco
    try:
        from app.database import test_connection
        health_data["database"] = "connected" if test_connection() else "disconnected"
    except ImportError:
        health_data["database"] = "module_not_found"
    except Exception as e:
        health_data["database"] = f"error: {str(e)}"

    return health_data


@app.get("/info", summary="Get Info", description="Informações detalhadas da API")
async def get_info():
    """Informações detalhadas da API"""
    return {
        "name": "CarWash API",
        "version": "1.0.0",
        "description": "API para agendamento de lava-jatos",
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "endpoints": {
            "auth": "/auth/*" if "auth" in loaded_routers else "❌ Não carregado",
            "users": "/user/*" if "user" in loaded_routers else "❌ Não carregado",
            "car_washes": "/car-wash/*" if "car_wash" in loaded_routers else "❌ Não carregado",
            "services": "/service/*" if "service" in loaded_routers else "❌ Não carregado",
            "bookings": "/booking/*" if "booking" in loaded_routers else "❌ Não carregado",
            "reviews": "/review/*" if "review" in loaded_routers else "❌ Não carregado"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "routers_status": {
            "loaded": loaded_routers,
            "failed": failed_routers
        }
    }


@app.get("/debug", summary="Debug Info", description="Informações de debug (apenas desenvolvimento)")
async def debug_info():
    """Informações de debug para desenvolvimento"""
    return {
        "python_path": sys.path[:5],  # Primeiros 5 caminhos
        "current_directory": os.getcwd(),
        "app_directory_exists": os.path.exists("app"),
        "routes_directory_exists": os.path.exists("app/routes"),
        "files_in_app": os.listdir("app") if os.path.exists("app") else "❌ app/ não existe",
        "files_in_routes": os.listdir("app/routes") if os.path.exists("app/routes") else "❌ app/routes/ não existe",
        "loaded_routers": loaded_routers,
        "failed_routers": failed_routers
    }


@app.get("/routes-debug", summary="Routes Debug", description="Lista todas as rotas registradas")
async def routes_debug():
    """Lista todas as rotas registradas"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', 'N/A'),
                "tags": getattr(route, 'tags', [])
            })
    return {
        "total_routes": len(routes),
        "routes": sorted(routes, key=lambda x: x['path']),
        "routers_loaded": loaded_routers,
        "routers_failed": failed_routers
    }


# ========================
# HANDLER DE ERROS
# ========================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint não encontrado",
            "message": f"O endpoint {request.url.path} não existe",
            "available_endpoints": ["/", "/health", "/info", "/debug", "/docs"]
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"❌ Erro interno: {exc}")
    logger.error(f"🔍 Traceback: {traceback.format_exc()}")

    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "message": "Ocorreu um erro inesperado. Verifique os logs."
        }
    )


# ========================
# DESENVOLVIMENTO LOCAL
# ========================
if __name__ == "__main__":
    import uvicorn

    logger.info("🔧 Modo desenvolvimento - iniciando servidor...")
    logger.info("📍 Execute com: uvicorn main:app --reload")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )