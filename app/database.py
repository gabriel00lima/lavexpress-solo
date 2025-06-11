# test_db.py
import psycopg2
from decouple import config


def test_connection():
    try:
        # Usar a URL do .env ou conexão direta
        conn = psycopg2.connect(
            host="localhost",
            database="carwash_db",
            user="postgres",
            password=config('DATABASE_PASSWORD', default='Cabideverde10')
        )

        cursor = conn.cursor()

        # Testar conexão
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
        print("✅ Conexão com PostgreSQL bem-sucedida!")
        print(f"Versão: {result[0]}")

        # Testar extensão UUID
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'uuid-ossp';")
        uuid_ext = cursor.fetchone()
        if uuid_ext:
            print("✅ Extensão uuid-ossp instalada!")
        else:
            print("❌ Extensão uuid-ossp não encontrada!")

        # Testar geração de UUID
        cursor.execute("SELECT gen_random_uuid();")
        uuid_result = cursor.fetchone()
        print(f"✅ UUID gerado: {uuid_result[0]}")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False


if __name__ == "__main__":
    test_connection()