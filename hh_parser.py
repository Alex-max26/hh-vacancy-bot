# hh_parser.py (обновлённый)
import requests

def search_vacancies(text, area, min_salary=None):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": text,
        "area": area,
        "per_page": 10,  # Увеличим, чтобы отфильтровать по ЗП
        "order_by": "publication_time"
    }
    if min_salary:
        params["salary"] = min_salary
        params["only_with_salary"] = "true"

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return None

        data = response.json()
        vacancies = data.get("items", [])
        return [
            {
                "hh_id": v["id"],  # Добавили ID
                "title": v["name"],
                "salary": format_salary(v.get("salary")),
                "url": v["alternate_url"],
                "employer": v["employer"]["name"],
            }
            for v in vacancies
        ]
    except Exception as e:
        print(f"Ошибка при поиске вакансий: {e}")
        return None

def format_salary(salary):
    if not salary:
        return "Не указана"
    from_ = salary.get("from")
    to_ = salary.get("to")
    currency = salary.get("currency", "")
    parts = []
    if from_:
        parts.append(f"от {from_}")
    if to_:
        parts.append(f"до {to_}")
    if parts:
        return " ".join(parts) + f" {currency}"
    return "Не указана"
