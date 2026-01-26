# database.py
import sqlite3
import os

DB_NAME = "vacancies.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                id INTEGER PRIMARY KEY,
                hh_id TEXT UNIQUE,
                title TEXT,
                employer TEXT,
                salary TEXT,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def save_vacancy(vacancy_data):
    with sqlite3.connect(DB_NAME) as conn:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO vacancies (hh_id, title, employer, salary, url)
                VALUES (?, ?, ?, ?, ?)
            """, (
                vacancy_data['hh_id'],
                vacancy_data['title'],
                vacancy_data['employer'],
                vacancy_data['salary'],
                vacancy_data['url']
            ))
        except Exception as e:
            print(f"Ошибка при сохранении в БД: {e}")

def get_new_vacancies(vacancies_list):
    new_jobs = []
    with sqlite3.connect(DB_NAME) as conn:
        for job in vacancies_list:
            hh_id = job['hh_id']
            cursor = conn.execute("SELECT 1 FROM vacancies WHERE hh_id = ?", (hh_id,))
            if cursor.fetchone() is None:
                new_jobs.append(job)
    return new_jobs
