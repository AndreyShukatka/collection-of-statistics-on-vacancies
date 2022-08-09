import os
from dotenv import load_dotenv

import requests
import terminaltables


def calculate_salary(payment_from, payment_to):
    salary = 0
    if payment_to and payment_from:
        salary = int((payment_to + payment_from) // 2)
    elif payment_to:
        salary = int(payment_to * 0.8)
    elif payment_from:
        salary = int(payment_from * 1.2)
    return salary


# Функции для hh.ru:


def get_request_hhru(language, url_hh, page=None):
    city_id = 1
    per_page = 100
    params_all_days = {
        'text': f'Программист {language}',
        'area': city_id,
        'only_with_salary': 'True',
        'currency': 'RUR',
        'page': page,
        'per_page': per_page
    }
    response = requests.get(url_hh, params=params_all_days)
    response.raise_for_status()
    vacancy_response = response.json()
    total_vacancies = vacancy_response.get('found')
    requested_vacancies = vacancy_response.get('items')
    pages_amount = vacancy_response.get('pages')
    return total_vacancies, requested_vacancies, pages_amount


def predict_rub_salary_hhru(requested_vacancies):
    vacancies_processed = 0
    total_salary = 0
    total_salary_all = 0
    for vacancy in requested_vacancies:
        vacancy_salary = vacancy.get('salary')
        if vacancy_salary.get('currency') != 'RUR':
            continue
        salary = calculate_salary(
            vacancy['salary']['from'], vacancy['salary']['to']
        )
        if not salary:
            continue
        vacancies_processed += 1
        total_salary += salary
    try:
        average_salary = int(total_salary // vacancies_processed)
        total_salary_all += average_salary
        return average_salary, vacancies_processed
    except ZeroDivisionError:
        raise ZeroDivisionError('Деление на 0 запрещено')


def get_average_salaries_hhru(program_languages, url_hh):
    vacancies_jobs = {}
    for language in program_languages:
        vacancy_summary = []
        page = 0
        pages_amount = 1
        while page < pages_amount:
            total_vacancies, requested_vacancies, pages_amount =\
                get_request_hhru(language, url_hh, page=page)
            vacancy_summary.extend(requested_vacancies)
            page += 1
        average_salary, vacancies_processed = predict_rub_salary_hhru(
                vacancy_summary
            )
        vacancies_jobs[language] = {
            'vacancies_found': total_vacancies,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary
        }
    return vacancies_jobs


# Функции для superjoba:


def predict_rub_salary_for_superjob(vacancies):
    vacancies_processed = 0
    total_salary = 0
    for vacancy in vacancies:
        if vacancy['currency'] != 'rub':
            continue
        salary = calculate_salary(
            vacancy['payment_from'], vacancy['payment_to']
        )
        if not salary:
            continue
        vacancies_processed += 1
        total_salary += salary
    try:
        average_salary = int(total_salary // vacancies_processed)
        return average_salary, vacancies_processed
    except ZeroDivisionError:
        raise ZeroDivisionError('Деление на 0 запрещено')


def get_request_superjob(superjob_token, superjob_auth, language, page):
    city_id = 4
    page_count = 100
    agreement_status = 1
    header = {
        'X-Api-App-Id': superjob_token,
        'Authorization': superjob_auth,
    }
    params = {
        'keywords': language,
        'town': city_id,
        'no_agreement': agreement_status,
        'page': page,
        'count': page_count
    }
    response = requests.get(url_superjob, headers=header, params=params)
    response.raise_for_status()
    server_response = response.json()
    total_vacancies = server_response.get('total')
    requested_vacancies = server_response.get('objects')
    next_page_flag = server_response.get('more')
    return total_vacancies, requested_vacancies, next_page_flag


def get_average_salaries_superjob(
        program_languages, superjob_key, superjob_auth
):
    vacancies_jobs = dict()
    for language in program_languages:
        vacancies_summary = []
        next_page_flag = True
        page = 0
        while next_page_flag:
            total_vacancies, requested_vacancies, next_page_flag =\
                get_request_superjob(
                    superjob_key, superjob_auth, language, page
                )
            vacancies_summary.extend(requested_vacancies)
            page += 1
        average_salary, vacancies_processed = \
            predict_rub_salary_for_superjob(vacancies_summary)
        vacancies_jobs[language] = {
            'vacancies_found': total_vacancies,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary
        }
    return vacancies_jobs


def get_vacancies_table(site_name, statistic):
    title = site_name
    vacancies_table = [[
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата'
    ]]
    for lang, stats in statistic.items():
        row = [lang]
        for key, value in stats.items():
            row.append(value)
        vacancies_table.append(row)
    table = terminaltables.AsciiTable(vacancies_table, title=title)
    return table.table


if __name__ == '__main__':
    load_dotenv()
    superjob_auth = os.environ['SUPERJOB_AUTH']
    superjob_key = os.environ['SUPERJOB_KEY']
    program_languages = [
         'C++', 'PHP', 'Ruby', 'Python', 'Java', 'JavaScript'
    ]
    url_hh = 'https://api.hh.ru/vacancies'
    url_superjob = 'https://api.superjob.ru/2.0/vacancies/'

    # Таблица SuperJob:
    site_name = 'SuperJob Moscow'
    statistic = get_average_salaries_superjob(
        program_languages, superjob_key, superjob_auth
    )
    print(get_vacancies_table(site_name, statistic))

    # Таблица HeadHunter:
    site_name = 'HeadHunter Moscow'
    statistic = get_average_salaries_hhru(program_languages, url_hh)
    print(get_vacancies_table(site_name, statistic))
