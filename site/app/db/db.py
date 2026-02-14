import os
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models import *
import atexit
import logging, time
from decimal import Decimal

connection_string = os.environ.get('db_url_connect_remote')
engine = create_engine(connection_string)

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

# Пример проверки подключения
with engine.connect() as conn:
    print("Успешное подключение к базе данных!")
Session = sessionmaker(engine)
session = Session()

def close_other_sessions():
    """Закрывает все сессии базы данных кроме текущей"""
    try:
        with engine.connect() as conn:
            # Получаем имя текущей базы данных из connection string
            db_name = connection_string.split('/')[-1]

            # Завершаем все сессии кроме текущей
            query = text("""
                SELECT pg_terminate_backend(pid) 
                FROM pg_stat_activity 
                WHERE datname = :db_name 
                AND pid <> pg_backend_pid()
                AND state = 'active'
            """)

            result = conn.execute(query, {'db_name': db_name})
            closed_sessions = result.rowcount
            print(f"Завершено {closed_sessions} сессий")

            conn.commit()

    except Exception as e:
        print(f"Ошибка при закрытии сессий: {e}")


def shutdown_database():
    """Корректное завершение работы с БД"""
    logging.info("Начинаем корректное завершение работы с БД...")

    try:
        # Закрываем все активные сессии
        close_other_sessions()
        session.commit()
        session.close()

        # Закрываем пул соединений
        engine.dispose()

        logging.info("База данных успешно закрыта. Сервер можно выключать.")

    except Exception as e:
        logging.error(f"Ошибка при завершении работы с БД: {e}")