import requests


class HeadHunterAPI:
    """ Implementation of a class for loading vacancies and employers from an external resource - HH.ru """

    def __init__(self, settings):
        """ Set basic settings and variables of the class  instance. """
        self.employers_url = settings['employers_url']
        self.per_page = settings['per_page']
        self.employers_per_page = settings['employers_per_page']
        self.area = settings['area']

    def get_vacancies_by_employer(self, vacancies_url):
        """ Implementation of a method for loading vacancies for employer from his url. """

        params = {
            'per_page': self.per_page,
            'page': 0,
            'pages': 10000,
        }

        result = list()

        while params['page'] < params['pages']:
            response = requests.get(vacancies_url, params)
            if response.status_code == 200:
                response_json = response.json()
                params['page'] = int(response_json['page']) + 1
                params['pages'] = int(response_json['pages'])
                result.extend(response_json['items'])
            else:
                break

        return result

    def get_employers(self, search_text):
        """ Implementation of a method for loading employers using a search query. """

        params = {
            'per_page': self.employers_per_page,
            'page': 0,
            'text': search_text,
            'only_with_vacancies': True,
            'sort_by': 'by_vacancies_open',
            'area': self.area
        }

        result = list()

        response = requests.get(self.employers_url, params)
        if response.status_code == 200:
            response_json = response.json()
            result.extend(response_json['items'])

        return result
