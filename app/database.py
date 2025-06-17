# app/database.py
import logging
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from decouple import config

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações do banco de dados
DATABASE_URL = config('DATABASE_URL')
DATABASE_ECHO = config('DATABASE_ECHO', default=False, cast=bool)

# Configurações avançadas do pool de conexões
POOL_SIZE = config('DB_POOL_SIZE', default=5, cast=int)
MAX_OVERFLOW = config('DB_MAX_OVERFLOW', default=10, cast=int)
POOL_TIMEOUT = config('DB_POOL_TIMEOUT', default=30, cast=int)
POOL_RECYCLE = config('DB_POOL_RECYCLE', default=3600, cast=int)  # 1 hora

# Criar engine com configurações otimizadas
engine = create_engine(
    DATABASE_URL,
    echo=DATABASE_ECHO,
    poolclass=QueuePool,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=True,  # Verifica conexões antes de usar
    connect_args={
        "options": "-c timezone=America/Sao_Paulo"  # Define timezone
    }
)

# Configurar SessionLocal
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Mantém objetos após commit
)

# Base para os modelos
Base = declarative_base()


# Eventos do SQLAlchemy para logging
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Configurações específicas para conexão do banco"""
    if 'postgresql' in str(engine.url):
        # Configurações específicas do PostgreSQL
        with dbapi_connection.cursor() as cursor:
            # Habilita extensão uuid-ossp se não estiver habilitada
            try:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
                dbapi_connection.commit()
            except Exception as e:
                logger.warning(f"Não foi possível criar extensão uuid-ossp: {e}")


@event.listens_for(engine, "first_connect")
def receive_first_connect(dbapi_connection, connection_record):
    """Executado na primeira conexão"""
    logger.info("Primeira conexão com o banco de dados estabelecida")


def get_db():
    """
    Dependency para obter sessão do banco de dados
    Usado em rotas FastAPI com Depends()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Erro na sessão do banco: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """Cria todas as tabelas no banco de dados"""
    try:
        logger.info("Criando tabelas no banco de dados...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        raise


def drop_tables():
    """Remove todas as tabelas do banco de dados"""
    try:
        logger.warning("Removendo todas as tabelas...")
        Base.metadata.drop_all(bind=engine)
        logger.info("Tabelas removidas com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao remover tabelas: {e}")
        raise


def test_connection():
    """Testa a conexão com o banco de dados"""
    try:
        db = SessionLocal()
        # CORREÇÃO: Usar text() para SQL puro
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Conexão com banco de dados OK!")
        return True
    except Exception as e:
        logger.error(f"Erro na conexão com banco: {e}")
        return False


def get_database_info():
    """Retorna informações sobre o banco de dados"""
    try:
        db = SessionLocal()

        # Informações básicas
        result = db.execute(text("SELECT version()")).fetchone()
        db_version = result[0] if result else "Desconhecida"

        # Verifica extensões (PostgreSQL)
        extensions = []
        try:
            ext_result = db.execute(
                text("SELECT extname FROM pg_extension ORDER BY extname")
            ).fetchall()
            extensions = [row[0] for row in ext_result]
        except:
            pass

        db.close()

        return {
            "database_url": DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL,
            "version": db_version,
            "extensions": extensions,
            "pool_size": POOL_SIZE,
            "max_overflow": MAX_OVERFLOW
        }

    except Exception as e:
        logger.error(f"Erro ao obter informações do banco: {e}")
        return {"error": str(e)}


# Context manager para transações
class DatabaseTransaction:
    """Context manager para transações de banco de dados"""

    def __init__(self):
        self.db = None

    def __enter__(self):
        self.db = SessionLocal()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(f"Erro na transação: {exc_val}")
            self.db.rollback()
        else:
            self.db.commit()
        self.db.close()


# Função para executar queries raw de forma segura
def execute_raw_query(query: str, params: dict = None):
    """Executa query SQL raw de forma segura"""
    try:
        with DatabaseTransaction() as db:
            result = db.execute(text(query), params or {})
            return result.fetchall()
    except Exception as e:
        logger.error(f"Erro na execução de query: {e}")
        raise


# Inicialização automática para desenvolvimento
if __name__ == "__main__":
    print("Testando conexão com banco de dados...")
    if test_connection():
        print("✅ Conexão OK!")
        info = get_database_info()
        print(f"📊 Informações do banco: {info}")
    else:
        print("❌ Falha na conexão!")
        exit(1)
