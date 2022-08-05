import os
from dotenv import load_dotenv
from itertools import count

import requests
import terminaltables


# Функции для hh.ru:


def search_vacations_hhru(language, url_hh, page=None):
    params_all_days = {
        'text': f'Программист {language}',
        'area': '1',
        'only_with_salary': 'True',
        'currency': 'RUR',
        'page': page
    }
    response_all_day = requests.get(url_hh, params=params_all_days)
    response_all_day.raise_for_status()
    vacancy_all_days = response_all_day.json()
    return vacancy_all_days


def add_vacancy_hhru(vacations, language):
    url = 'https://api.hh.ru/vacancies'
    params_all_days = {
        'text': f'Программист {language}',
        'area': '1',
        'only_with_salary': 'True',
        'currency': 'RUR'
    }
    response_all_day = requests.get(url, params=params_all_days)
    vacancy_all_days = response_all_day.json()
    for vacancy_info in vacancy_all_days['items']:
        vacations.append(vacancy_info)


def predict_rub_salary_hhru(language, url_hh):
    predictioned_salaries = []
    try:
        for vacancy_salary in get_salaries_bracket_hhru(language, url_hh):
            if vacancy_salary['to']\
                    and vacancy_salary['from']:
                salary = (int(vacancy_salary['to']) + int(vacancy_salary['from'])) // 2
                predictioned_salaries.append(salary)
            elif vacancy_salary['from']:
                salary = int(vacancy_salary['from']) * 0.8
                predictioned_salaries.append(int(salary))
            elif vacancy_salary['to']:
                salary = int(vacancy_salary['to']) * 1.2
                predictioned_salaries.append(int(salary))
    except TypeError:
        predictioned_salaries.append(None)
    return predictioned_salaries


def get_salaries_bracket_hhru(language, url_hh):
    salaries_bracket = []
    for page in count(0):
        vacations = search_vacations_hhru(language, url_hh, page=page)
        for salary in vacations['items']:
            salaries_bracket.append(salary['salary'])
        if page >= vacations['pages']:
            break
    return salaries_bracket


def average_salaries_hhru(program_languages, url_hh):
    vacancies_jobs = {}
    for language in program_languages:
        total_vacancies = search_vacations_hhru(language, url_hh, page=None)
        predictioned_salaries = predict_rub_salary_hhru(language, url_hh)
        summary = int(sum(predictioned_salaries))\
            // int(len(predictioned_salaries))
        vacancies_jobs[language] = {
            'vacancies_found': total_vacancies['found'],
            'vacancies_processed': len(predictioned_salaries),
            'average_salary': summary
        }
    return vacancies_jobs


# Функции для superjoba:


def predict_rub_salary_for_superjob(language):
    predictioned_salaries = []
    vacancys = add_vacancys_superjob(language)
    for vacancy in vacancys:
        payment_to = vacancy['payment_to']
        payment_from = vacancy['payment_from']
        if payment_to and payment_from != 0:
            average_salary = (payment_to + payment_from) // 2
            predictioned_salaries.append(average_salary)
        elif payment_to > 0:
            average_salary = int(payment_to * 0.8)
            predictioned_salaries.append(int(average_salary))
        elif payment_from > 0:
            average_salary = payment_from * 1.2
            predictioned_salaries.append(int(average_salary))
        else:
            average_salary = None
            predictioned_salaries.append(average_salary)
    return predictioned_salaries


def request_superjob(superjob_token, superjob_auth, language):
    header = {
        'X-Api-App-Id': superjob_token,
        'Authorization': superjob_auth,
    }
    params = {
        'keywords': language,
        'town': 4,
        'no_agreement': 1
    }
    response = requests.get(url_superjob, headers=header, params=params).json()
    return response


def add_vacancys_superjob(language):
    vacancys = []
    for vacancy in request_superjob(
            superjob_key, superjob_auth, language
    )['objects']:
        vacancys.append(vacancy)
    return vacancys


def get_average_salaries_superjob(program_languages):
    vacancies_jobs = dict()
    for language in program_languages:
        predictioned_salaries = predict_rub_salary_for_superjob(language)
        average_salary = int(sum(predictioned_salaries)) \
            // int(len(predictioned_salaries))
        total = request_superjob(superjob_key, superjob_auth, language)['total']
        vacancies_jobs[language] = {
            'vacancies_found': total,
            'vacancies_processed': len(predictioned_salaries),
            'average_salary': average_salary
        }
    return vacancies_jobs


def make_table(site_name, statistic):
    title = site_name
    table_data = [[
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата'
    ]]
    for lang, stats in statistic.items():
        row = [lang]
        for key, value in stats.items():
            row.append(value)
        table_data.append(row)
    table = terminaltables.AsciiTable(table_data, title=title)
    return table.table


if __name__ == '__main__':
    load_dotenv()
    superjob_auth = os.environ['AUTHORIZATION']
    superjob_key = os.environ['X_API_APP_ID']
    program_languages = [
        'Go', 'C++', 'PHP', 'Ruby', 'Python', 'Java', 'JavaScript'
    ]
    url_hh = 'https://api.hh.ru/vacancies'
    url_superjob = 'https://api.superjob.ru/2.0/vacancies/'
    site_name = 'SuperJob Moscow'
    # Таблица SuperJob:
    statistic = get_average_salaries_superjob(program_languages)
    print(make_table(site_name, statistic))

    # Таблица HeadHunter:
    site_name = 'HeadHunter Moscow'
    statistic = average_salaries_hhru(program_languages, url_hh)
    print(make_table(site_name, statistic))
