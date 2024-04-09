from classes.api import HeadHunterAPI


def get_salary2human(salary_from, salary_to):
    """ Returns the salary in human-readable form. """
    salary_from = int(salary_from)
    salary_to= int(salary_to)
    if salary_from == 0:
        salary_from = salary_to
    if salary_to == 0:
        salary_to = salary_from
    if salary_from == 0 and salary_to == 0:
        return "не указана"
    if salary_from != salary_to:
        return f"{salary_from} - {salary_to}"
    return str(salary_from)


def print_employers(employers):
    """ Shows a list of employers. """

    print("\n")
    for n, employer in enumerate(employers):
        print(f"{n + 1}. {employer['name']}, вакансий: {employer['open_vacancies']}")


def print_vacancies(vacancies, detail="2"):
    """ Show list of vacancies (details on request). """

    print("\n")
    for n, vacancy in enumerate(vacancies):
        print(f"{n + 1}. {vacancy['name']}, город: {vacancy['area']}, зарплата: {get_salary2human(vacancy['salary_from'], vacancy['salary_to'])}")
        if detail == "1":
            print(f"\tСсылка: \n\t\t{vacancy['alternate_url']}")
            print(f"\tОписание: \n\t\t{vacancy['snippet']}")
            print(f"\tРаботадатель: \n\t\t{vacancy['employer_name']}")


def get_employers_vacancies(hh_api: HeadHunterAPI, employers):
    """ For each employer we get a list of vacancies and combine them into a common list. """

    vacancies = []
    for employer in employers:
        vacancies.extend(hh_api.get_vacancies_by_employer(employer['vacancies_url']))
    return vacancies
