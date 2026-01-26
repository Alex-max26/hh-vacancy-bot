# bot.py
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import sqlite3  # можно убрать, если не используешь напрямую

from hh_parser import search_vacancies
from database import init_db, get_new_vacancies, save_vacancy  # ← ЭТО ВАЖНО!
import config


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я помогу найти вакансии 🚀\n"
        "Напиши город и профессию, например:\n"
        "Москва Python"
    )

# bot.py — обновлённая функция
async def find_vacancies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    if len(query.split()) < 2:
        await update.message.reply_text("Введите город и профессию, например: Москва Python")
        return

    # Разбиваем запрос
    parts = query.split()
    city = parts[0]
    job_query = " ".join(parts[1:])

    # Города → ID
    area_map = {
        "москва": 1,
        "спб": 2, "петербург": 2, "санкт-петербург": 2,
        "екатеринбург": 3,
        "новосибирск": 4,
        "казань": 87,
        "самара": 64,
    }
    area = area_map.get(city.lower(), 1)

    # Фильтр по ЗП (если есть числа)
    min_salary = None
    if "от" in query.lower():
        import re
        salary_match = re.search(r"от\s+(\d+)", query, re.IGNORECASE)
        if salary_match:
            try:
                min_salary = int(salary_match.group(1))
            except:
                pass

    await update.message.reply_text(
        f"🔍 Ищу вакансии: <b>{job_query}</b> в {city}"
        + (f" с ЗП от {min_salary} ₽" if min_salary else ""),
        parse_mode="HTML"
    )

    # Поиск вакансий
    jobs = search_vacancies(job_query, area, min_salary=min_salary)
    if not jobs:
        await update.message.reply_text("❌ Ничего не найдено.")
        return

    # Фильтр: только новые
    new_jobs = get_new_vacancies(jobs)
    saved_count = 0

    if new_jobs:
        for job in new_jobs:
            save_vacancy(job)
            saved_count += 1
            message = f"""
✨ <b>{job['title']}</b>
🏢 {job['employer']}
💰 {job['salary']}
🔗 <a href="{job['url']}">Смотреть вакансию</a>
            """.strip()
            await update.message.reply_html(message)

        await update.message.reply_text(
            f"✅ Новых вакансий: {len(new_jobs)} из {len(jobs)}\n"
            "Все они сохранены в базу."
        )
    else:
        await update.message.reply_text("📭 Новых вакансий пока нет. Все уже показаны ранее.")

def main():
    init_db()
    app = Application.builder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, find_vacancies))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
