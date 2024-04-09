import psycopg2
import psycopg2.extras

from psycopg2 import Error


class DBManager:
    """ """

    def __init__(self, params, dbname):
        self.params = params
        self.dbname = dbname
        self.conn = None

        # self.conn = self.create_database(self.dbname)

    def __del__(self):
        if self.conn:
            self.conn.close()

    def exists_db(self):
        conn = psycopg2.connect(dbname="postgres", **self.params)
        conn.autocommit = True
        cur = conn.cursor()
        try:
            cur.execute("SELECT pg_database_size(%s);", (self.dbname,))
        except Error as e:
            return False
        finally:
            cur.close()
            conn.close()
        return True

    def create_database(self):
        try:
            conn = psycopg2.connect(dbname="postgres", **self.params)
            conn.autocommit = True
            cur = conn.cursor()

            # cur.execute("SELECT pg_database_size(%s);", (self.dbname, ))

            cur.execute(f"DROP DATABASE IF EXISTS {self.dbname}")
            cur.execute(f"CREATE DATABASE {self.dbname}")

            conn.close()

            conn = psycopg2.connect(dbname=self.dbname, **self.params)

            with conn.cursor() as cur:
                cur.execute("""
                        CREATE TABLE employers (
                            id INTEGER PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            vacancies_url VARCHAR(255) NOT NULL,
                            open_vacancies INTEGER NOT NULL
                        )
                    """)

            with conn.cursor() as cur:
                cur.execute("""
                        CREATE TABLE vacancies (
                            id INTEGER PRIMARY KEY,
                            employer_id INT REFERENCES employers(id),
                            name VARCHAR(255) NOT NULL,
                            area VARCHAR NOT NULL,
                            salary_from INTEGER,
                            salary_to INTEGER,
                            snippet TEXT,
                            schedule VARCHAR(100),
                            alternate_url VARCHAR(256)
                        )
                    """)

            conn.commit()
            # conn.close()

            # return conn  # psycopg2.connect(dbname=database_name, **self.params)
        except Error as e:
            print(e)

    def open_db(self):
        self.conn = psycopg2.connect(dbname=self.dbname, **self.params)

    def save_employers(self, employers):
        with self.conn.cursor() as cur:
            for employer in employers:
                try:
                    cur.execute("""INSERT INTO employers (id, name, vacancies_url, open_vacancies)
                               VALUES (%s, %s, %s, %s)""",
                            (employer['id'],
                             employer['name'],
                             employer['vacancies_url'],
                             employer['open_vacancies']))
                except:
                    ...
        self.conn.commit()

    def save_vacancies(self, vacancies):
        with self.conn.cursor() as cur:
            for vacancy in vacancies:

                    cur.execute("""INSERT INTO vacancies
                               (id, employer_id, name, area, salary_from, salary_to, snippet, schedule, alternate_url)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                (vacancy['id'],
                                 vacancy['employer']['id'],
                                 vacancy['name'],
                                 vacancy['area']['name'],
                                 (vacancy['salary'] or {}).get('from') or 0,
                                 (vacancy['salary'] or {}).get('to') or 0,
                                 (vacancy['snippet']['requirement'] or '') + (vacancy['snippet']['responsibility'] or ''),
                                 vacancy['schedule']['name'],
                                 vacancy['alternate_url']
                                 )
                    )

        self.conn.commit()

    def get_companies_and_vacancies_count(self):
        """ Gets a list of all companies and the number of vacancies for each company. """

        result = []
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM employers ORDER BY name")
            ans = cur.fetchall()
            for row in ans:
                result.append(dict(row))
        return result

    def get_all_vacancies(self):
        """ Receives a list of all vacancies indicating the company name,
         vacancy title and salary and a link to the vacancy. """

        result = []
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
               SELECT
                   vacancies.*, employers.name as employer_name
               FROM vacancies
               JOIN employers ON vacancies.employer_id=employers.id 
               ORDER BY vacancies.name
            """)
            ans = cur.fetchall()
            for row in ans:
                result.append(dict(row))
        return result

    def get_avg_salary(self):
        """ Receives average salary for vacancies. """

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT AVG(GREATEST(salary_from , salary_to))
                FROM vacancies
                WHERE salary_from != 0 AND salary_to != 0""")
            return round(cur.fetchone()[0], 2)

    def get_vacancies_with_higher_salary(self):
        """ Gets a list of all vacancies whose salary is higher than the average for all vacancies. """

        avg_salary = self.get_avg_salary()
        result = []
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT
                    vacancies.*, employers.name as employer_name
                FROM vacancies
                JOIN employers ON vacancies.employer_id=employers.id
                WHERE GREATEST(salary_from , salary_to) >= %s
                ORDER BY vacancies.name
            """, (avg_salary, ))
            ans = cur.fetchall()
            for row in ans:
                result.append(dict(row))
        return result

    def get_vacancies_with_keyword(self, user_search):
        """ Gets a list of all vacancies whose titles contain the words passed to the method, for example 'python'. """

        result = []
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                        SELECT
                            vacancies.*, employers.name as employer_name
                        FROM vacancies
                        JOIN employers ON vacancies.employer_id=employers.id
                        WHERE LOWER(vacancies.name) LIKE %s
                        ORDER BY vacancies.name
                    """, (f"%{user_search}%",))
            ans = cur.fetchall()
            for row in ans:
                result.append(dict(row))
        return result
