# init_db.py
"""
Script para inicializar o banco de dados com dados de exemplo
Execute com: python init_db.py
"""

import sys
import os
from datetime import time, datetime, date, timedelta
from decimal import Decimal

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import create_tables, test_connection, SessionLocal
from app.models.user import User
from app.models.car_wash import CarWash
from app.models.service import Service
from app.models.booking import Booking, BookingStatus
from app.models.review import Review
from app.services.core.security import get_password_hash


def create_sample_users(db):
    """Cria usuários de exemplo"""
    print("Criando usuários de exemplo...")

    users_data = [
        {
            "nome": "João Silva",
            "email": "joao@exemplo.com",
            "senha_hash": get_password_hash("123456"),
            "telefone": "(61) 99999-1111",
            "latitude": -15.7801,
            "longitude": -47.9292
        },
        {
            "nome": "Maria Santos",
            "email": "maria@exemplo.com",
            "senha_hash": get_password_hash("123456"),
            "telefone": "(61) 99999-2222",
            "latitude": -15.7901,
            "longitude": -47.9392
        },
        {
            "nome": "Pedro Oliveira",
            "email": "pedro@exemplo.com",
            "senha_hash": get_password_hash("123456"),
            "telefone": "(61) 99999-3333",
            "latitude": -15.7701,
            "longitude": -47.9192
        }
    ]

    users = []
    for user_data in users_data:
        user = User(**user_data)
        db.add(user)
        users.append(user)

    db.commit()
    print(f"✅ {len(users)} usuários criados!")
    return users


def create_sample_car_washes(db):
    """Cria lava-jatos de exemplo"""
    print("Criando lava-jatos de exemplo...")

    car_washes_data = [
        {
            "nome": "Auto Brilho Brasília",
            "descricao": "Lava-jato completo com enceramento e aspiração",
            "telefone": "(61) 3333-1111",
            "endereco": "SQN 102, Bloco A - Asa Norte, Brasília - DF",
            "latitude": -15.7651,
            "longitude": -47.8859,
            "nota": 4.5,
            "total_avaliacoes": 12,
            "imagem_url": "https://exemplo.com/auto-brilho.jpg",
            "aberto_de": time(8, 0),
            "aberto_ate": time(18, 0)
        },
        {
            "nome": "Lava Car Express",
            "descricao": "Serviço rápido e eficiente, ideal para o dia a dia",
            "telefone": "(61) 3333-2222",
            "endereco": "CLN 203, Bloco B - Asa Norte, Brasília - DF",
            "latitude": -15.7551,
            "longitude": -47.8959,
            "nota": 4.2,
            "total_avaliacoes": 8,
            "imagem_url": "https://exemplo.com/lava-express.jpg",
            "aberto_de": time(7, 0),
            "aberto_ate": time(19, 0)
        },
        {
            "nome": "Premium Wash",
            "descricao": "Serviços premium com produtos de alta qualidade",
            "telefone": "(61) 3333-3333",
            "endereco": "SQS 206, Bloco C - Asa Sul, Brasília - DF",
            "latitude": -15.8051,
            "longitude": -47.9159,
            "nota": 4.8,
            "total_avaliacoes": 25,
            "imagem_url": "https://exemplo.com/premium-wash.jpg",
            "aberto_de": time(8, 0),
            "aberto_ate": time(20, 0)
        },
        {
            "nome": "Eco Wash",
            "descricao": "Lavagem ecológica com produtos biodegradáveis",
            "telefone": "(61) 3333-4444",
            "endereco": "SHIS QI 7, Lago Sul - Brasília - DF",
            "latitude": -15.8251,
            "longitude": -47.8859,
            "nota": 4.3,
            "total_avaliacoes": 15,
            "imagem_url": "https://exemplo.com/eco-wash.jpg",
            "aberto_de": time(8, 30),
            "aberto_ate": time(17, 30)
        }
    ]

    car_washes = []
    for car_wash_data in car_washes_data:
        car_wash = CarWash(**car_wash_data)
        db.add(car_wash)
        car_washes.append(car_wash)

    db.commit()
    print(f"✅ {len(car_washes)} lava-jatos criados!")
    return car_washes


def create_sample_services(db, car_washes):
    """Cria serviços de exemplo"""
    print("Criando serviços de exemplo...")

    services_data = [
        # Auto Brilho Brasília
        {
            "nome": "Lavagem Simples",
            "descricao": "Lavagem externa com sabão neutro",
            "preco": Decimal("15.00"),
            "duracao_minutos": 30,
            "car_wash_id": car_washes[0].id
        },
        {
            "nome": "Lavagem Completa",
            "descricao": "Lavagem externa + aspiração interna",
            "preco": Decimal("25.00"),
            "duracao_minutos": 45,
            "car_wash_id": car_washes[0].id
        },
        {
            "nome": "Lavagem + Enceramento",
            "descricao": "Lavagem completa + enceramento da carroceria",
            "preco": Decimal("40.00"),
            "duracao_minutos": 60,
            "car_wash_id": car_washes[0].id
        },

        # Lava Car Express
        {
            "nome": "Express 15min",
            "descricao": "Lavagem rápida em 15 minutos",
            "preco": Decimal("12.00"),
            "duracao_minutos": 15,
            "car_wash_id": car_washes[1].id
        },
        {
            "nome": "Express Completo",
            "descricao": "Lavagem + aspiração rápida",
            "preco": Decimal("20.00"),
            "duracao_minutos": 25,
            "car_wash_id": car_washes[1].id
        },

        # Premium Wash
        {
            "nome": "Premium Basic",
            "descricao": "Lavagem com produtos premium",
            "preco": Decimal("30.00"),
            "duracao_minutos": 40,
            "car_wash_id": car_washes[2].id
        },
        {
            "nome": "Premium Deluxe",
            "descricao": "Serviço completo premium com cera importada",
            "preco": Decimal("60.00"),
            "duracao_minutos": 90,
            "car_wash_id": car_washes[2].id
        },
        {
            "nome": "Detalhamento Completo",
            "descricao": "Detalhamento interno e externo",
            "preco": Decimal("120.00"),
            "duracao_minutos": 180,
            "car_wash_id": car_washes[2].id
        },

        # Eco Wash
        {
            "nome": "Eco Básico",
            "descricao": "Lavagem ecológica básica",
            "preco": Decimal("18.00"),
            "duracao_minutos": 35,
            "car_wash_id": car_washes[3].id
        },
        {
            "nome": "Eco Completo",
            "descricao": "Lavagem + aspiração com produtos biodegradáveis",
            "preco": Decimal("28.00"),
            "duracao_minutos": 50,
            "car_wash_id": car_washes[3].id
        }
    ]

    services = []
    for service_data in services_data:
        service = Service(**service_data)
        db.add(service)
        services.append(service)

    db.commit()
    print(f"✅ {len(services)} serviços criados!")
    return services


def create_sample_bookings(db, users, services):
    """Cria agendamentos de exemplo"""
    print("Criando agendamentos de exemplo...")

    today = date.today()
    bookings_data = [
        # Agendamentos passados (concluídos)
        {
            "user_id": users[0].id,
            "car_wash_id": services[0].car_wash_id,
            "service_id": services[0].id,
            "data": today - timedelta(days=7),
            "hora": time(9, 0),
            "status": BookingStatus.CONCLUIDO,
            "observacoes": "Primeira vez aqui, adorei o serviço!"
        },
        {
            "user_id": users[1].id,
            "car_wash_id": services[4].car_wash_id,
            "service_id": services[4].id,
            "data": today - timedelta(days=3),
            "hora": time(14, 30),
            "status": BookingStatus.CONCLUIDO
        },

        # Agendamentos futuros
        {
            "user_id": users[0].id,
            "car_wash_id": services[6].car_wash_id,
            "service_id": services[6].id,
            "data": today + timedelta(days=2),
            "hora": time(10, 0),
            "status": BookingStatus.CONFIRMADO,
            "observacoes": "Por favor, dar atenção especial aos bancos de couro"
        },
        {
            "user_id": users[2].id,
            "car_wash_id": services[8].car_wash_id,
            "service_id": services[8].id,
            "data": today + timedelta(days=5),
            "hora": time(15, 0),
            "status": BookingStatus.PENDENTE
        },

        # Agendamento cancelado
        {
            "user_id": users[1].id,
            "car_wash_id": services[2].car_wash_id,
            "service_id": services[2].id,
            "data": today - timedelta(days=1),
            "hora": time(11, 0),
            "status": BookingStatus.CANCELADO,
            "observacoes": "Cancelado por imprevisto"
        }
    ]

    bookings = []
    for booking_data in bookings_data:
        booking = Booking(**booking_data)
        db.add(booking)
        bookings.append(booking)

    db.commit()
    print(f"✅ {len(bookings)} agendamentos criados!")
    return bookings


def create_sample_reviews(db, users, car_washes, bookings):
    """Cria avaliações de exemplo"""
    print("Criando avaliações de exemplo...")

    # Apenas para bookings concluídos
    completed_bookings = [b for b in bookings if b.status == BookingStatus.CONCLUIDO]

    reviews_data = [
        {
            "user_id": completed_bookings[0].user_id,
            "car_wash_id": completed_bookings[0].car_wash_id,
            "booking_id": completed_bookings[0].id,
            "nota": 5,
            "comentario": "Excelente serviço! Carro ficou impecável e o atendimento foi muito bom. Recomendo!"
        },
        {
            "user_id": completed_bookings[1].user_id,
            "car_wash_id": completed_bookings[1].car_wash_id,
            "booking_id": completed_bookings[1].id,
            "nota": 4,
            "comentario": "Serviço rápido e eficiente. Apenas a aspiração poderia ser mais detalhada."
        }
    ]

    reviews = []
    for review_data in reviews_data:
        review = Review(**review_data)
        db.add(review)
        reviews.append(review)

    db.commit()
    print(f"✅ {len(reviews)} avaliações criadas!")
    return reviews


def main():
    """Função principal de inicialização"""
    print("🚀 Iniciando configuração do banco de dados...")

    # Testa conexão
    if not test_connection():
        print("❌ Erro: Não foi possível conectar ao banco de dados!")
        print("Verifique se o PostgreSQL está rodando e as configurações estão corretas.")
        return False

    try:
        # Cria tabelas
        create_tables()

        # Cria sessão do banco
        db = SessionLocal()

        # Verifica se já existem dados
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"⚠️  Banco já contém {existing_users} usuários.")
            response = input("Deseja recriar os dados de exemplo? (s/N): ")
            if response.lower() not in ['s', 'sim', 'y', 'yes']:
                print("Abortado pelo usuário.")
                db.close()
                return True

            # Remove dados existentes
            print("Removendo dados existentes...")
            db.query(Review).delete()
            db.query(Booking).delete()
            db.query(Service).delete()
            db.query(CarWash).delete()
            db.query(User).delete()
            db.commit()

        # Cria dados de exemplo
        users = create_sample_users(db)
        car_washes = create_sample_car_washes(db)
        services = create_sample_services(db, car_washes)
        bookings = create_sample_bookings(db, users, services)
        reviews = create_sample_reviews(db, users, car_washes, bookings)

        db.close()

        print("\n🎉 Banco de dados inicializado com sucesso!")
        print("\n📊 Dados criados:")
        print(f"   👥 {len(users)} usuários")
        print(f"   🏪 {len(car_washes)} lava-jatos")
        print(f"   🔧 {len(services)} serviços")
        print(f"   📅 {len(bookings)} agendamentos")
        print(f"   ⭐ {len(reviews)} avaliações")

        print("\n🔑 Usuários de teste criados:")
        print("   📧 joao@exemplo.com - senha: 123456")
        print("   📧 maria@exemplo.com - senha: 123456")
        print("   📧 pedro@exemplo.com - senha: 123456")

        print("\n✅ Você pode agora iniciar a API com: uvicorn app.main:app --reload")

        return True

    except Exception as e:
        print(f"❌ Erro durante a inicialização: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)