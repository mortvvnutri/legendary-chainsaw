import os
import psycopg2
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

SQL_SCRIPT = """
CREATE TABLE IF NOT EXISTS "teams" (
    "team_id" bigint NOT NULL,
    "updated_at" timestamp with time zone NOT NULL,
    "login" varchar(255) NOT NULL UNIQUE,
    "password_hash" varchar(255) NOT NULL,
    "password_salt" varchar(255) NOT NULL,
    "created_at" timestamp with time zone NOT NULL,
    "status" varchar(20) DEFAULT 'offline',
    "viewed_tasks" bigint[] DEFAULT '{}',
    PRIMARY KEY ("team_id")
);

CREATE TABLE IF NOT EXISTS "task" (
    "task_id" bigint NOT NULL,
    "answer" jsonb NOT NULL,
    "qwestion" varchar(255) NOT NULL,
    "created_at" timestamp with time zone NOT NULL,
    PRIMARY KEY ("task_id")
);

CREATE TABLE IF NOT EXISTS "solution" (
    "solution_id" bigint NOT NULL,
    "condition" varchar(255) NOT NULL,
    "answer" jsonb NOT NULL,
    "sent_at" timestamp with time zone NOT NULL,
    "approved_at" timestamp with time zone,
    "team_id" bigint NOT NULL,
    "task_id" bigint NOT NULL,
    PRIMARY KEY ("solution_id"),
    CONSTRAINT "solution_fk5" FOREIGN KEY ("team_id") REFERENCES "teams"("team_id"),
    CONSTRAINT "solution_fk6" FOREIGN KEY ("task_id") REFERENCES "task"("task_id")
);
"""

def create_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(SQL_SCRIPT)
        cur.close()
        conn.close()
        print("✅ База данных успешно создана и инициализирована.")
    except Exception as e:
        print("❌ Ошибка при подключении к базе данных или выполнении запроса:", e)

if __name__ == "__main__":
    create_db()
