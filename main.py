from classes.api import HeadHunterAPI
from classes.dbmanager import DBManager
from config import config
from utils import print_employers, get_employers_vacancies, print_vacancies


def main():
    """ Main code for user interaction. """

    params = config(filename="database.ini", section="postgresql")
    settings = config(filename="settings.ini", section="api")

    db = DBManager(params, settings["dbname"])
    hh = HeadHunterAPI(settings)

    was_created = False
    if db.exists_db():
        print("База данных существует. Продолжить использовать (1) или пересоздать (0)")
        user_answer = input(">>> ")
        if user_answer == "0":
            db.create_database()
            was_created = True
    else:
        db.create_database()
        was_created = True
    db.open_db()

    if was_created:
        employers = hh.get_default_employers(settings['employers'])
        db.save_employers(employers)
        vacancies = get_employers_vacancies(hh, employers)
        db.save_vacancies(vacancies)
        print("Список работодателей и вакансий загружен.")

    while True:
        print("\nВыберите действие:")
        print("\t1. Добавить компании (топ 10)")
        print("\t2. Список всех компаний")
        print("\t3. Список всех вакансий")
        print("\t4. Средняя зарплата по вакансиям")
        print("\t5. Вакансии с зарплатой выше средней")
        print("\t6. Поиск вакансий по слову")
        print("\t0. Завершить")

        user_input = input(">>> ").strip()
        if user_input == "0":
            print("Программа завершена.")
            break

        elif user_input == "1":
            print("Введите строку для поиска:")
            user_search = input(">>> ").strip().lower()
            if not user_search:
                continue
            employers = hh.get_employers(user_search)
            if not employers:
                print("Ничего не нашли...\n")
                continue
            print_employers(employers)
            print("Сохранить эти компании и их вакансии в БД ? (1) - все, (2) - по одной, (0) - нет")
            user_answer = input(">>> ").strip()
            if user_answer == "1":
                db.save_employers(employers)
                vacancies = get_employers_vacancies(hh, employers)
                db.save_vacancies(vacancies)
            elif user_answer == "2":
                save_employers = []
                for employer in employers:
                    print_employers((employer, ))
                    print("Сохранить? (1) - да, (0) - нет")
                    user_yn = input(">>> ").strip()
                    if user_yn == "1":
                        save_employers.append(employer)
                db.save_employers(save_employers)
                vacancies = get_employers_vacancies(hh, save_employers)
                db.save_vacancies(vacancies)

        elif user_input == "2":
            print_employers(db.get_companies_and_vacancies_count())

        elif user_input == "3":
            print("Выводить подробную информацию? (1) - да, (2) - нет")
            user_answer = input(">>> ").strip()
            print_vacancies(db.get_all_vacancies(), user_answer)

        elif user_input == "4":
            print(f"Средняя зарплата: {db.get_avg_salary()}\n")

        elif user_input == "5":
            print_vacancies(db.get_vacancies_with_higher_salary())

        elif user_input == "6":
            print("Введите слово для поиска:")
            user_search = input(">>> ").strip().lower()
            if user_search:
                vacancies = db.get_vacancies_with_keyword(user_search)
                if vacancies:
                    print_vacancies(vacancies)
                else:
                    print("Ничего не нашли...\n")

        else:
            print("Проверьте правильность ввода...\n")


if __name__ == "__main__":
    main()
