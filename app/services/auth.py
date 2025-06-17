# corrigir_auth.py

print("🔧 CORRIGINDO ARQUIVO AUTH...")

# Novo conteúdo corrigido para auth.py
auth_content = '''# app/routes/auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import UserLogin, Token
from app.schemas.user import UserCreate, User as UserSchema
from app.crud.user import create_user, get_user_by_email, authenticate_user
from app.services.core.security import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    generate_password_reset_token,
    verify_password_reset_token,
    get_password_hash,
    validate_password_strength,
    verify_password
)
from app.services.core.config import settings
from app.services.core.dependencies import get_current_user

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registra um novo usuário"""

    # Verifica se email já existe
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )

    # Valida força da senha
    is_valid, message = validate_password_strength(user_data.senha)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    # Cria usuário
    try:
        user = create_user(db, user_data)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Autentica usuário e retorna tokens"""

    # Autentica usuário
    user = authenticate_user(db, login_data.email, login_data.senha)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Conta desativada",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Cria tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    refresh_token = create_refresh_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Renova o access token usando refresh token"""

    email = verify_refresh_token(refresh_token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresh inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_email(db, email)
    if not user or not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Cria novo access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/forgot-password")
async def forgot_password(email: str, db: Session = Depends(get_db)):
    """Inicia processo de recuperação de senha"""

    user = get_user_by_email(db, email)
    if not user:
        # Por segurança, sempre retorna sucesso mesmo se email não existir
        return {"message": "Se o email existir, você receberá instruções para redefinir sua senha"}

    # Gera token de reset
    reset_token = generate_password_reset_token(email)

    # TODO: Enviar email com o token de reset
    # Por enquanto, retorna o token (REMOVER EM PRODUÇÃO)
    return {
        "message": "Token de reset gerado",
        "reset_token": reset_token  # REMOVER EM PRODUÇÃO
    }


@router.post("/reset-password")
async def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    """Redefine senha usando token de reset"""

    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de reset inválido ou expirado"
        )

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    # Valida nova senha
    is_valid, message = validate_password_strength(new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    # Atualiza senha
    user.senha_hash = get_password_hash(new_password)
    db.commit()

    return {"message": "Senha redefinida com sucesso"}


@router.post("/change-password")
async def change_password(
        current_password: str,
        new_password: str,
        current_user: UserSchema = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Altera senha do usuário logado"""

    # Verifica senha atual
    if not verify_password(current_password, current_user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )

    # Valida nova senha
    is_valid, message = validate_password_strength(new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    # Atualiza senha
    current_user.senha_hash = get_password_hash(new_password)
    db.commit()

    return {"message": "Senha alterada com sucesso"}


@router.post("/logout")
async def logout():
    """Logout do usuário (blacklist do token seria implementado aqui)"""
    # TODO: Implementar blacklist de tokens se necessário
    return {"message": "Logout realizado com sucesso"}
'''

# Escrever o arquivo corrigido
with open("app/routes/auth.py", "w", encoding='utf-8') as f:
    f.write(auth_content)

print("✅ app/routes/auth.py corrigido!")

# Testar importação
try:
    from app.routes import auth
    print("✅ Auth importado com sucesso!")
    print("🎉 PROBLEMA RESOLVIDO!")
    print("✅ Execute: uvicorn app.main:app --reload")
except Exception as e:
    print(f"❌ Erro: {e}")

input("Pressione Enter...")