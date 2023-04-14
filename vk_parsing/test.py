import requests
import datetime


def all_dates():
    end_date = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - datetime.timedelta(days=365)

    delta = datetime.timedelta(hours=3)

    while end_date > start_date:
        start_time = int((end_date - delta).timestamp())
        end_time = int(end_date.timestamp())
        print(start_time, end_time)
        get_total_count(start_time, end_time)
        end_date -= delta


def get_total_count(start_time, end_time):
    # ключ доступа API
    ACCESS_TOKEN = ''

    # заголовки для запроса
    HEADERS = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }

    url = 'https://api.vk.com/method/newsfeed.search'

    params = {
        'v': '5.131',
        'q': 'Вкусно - и точка',
        'start_time': start_time,
        'end_time': end_time,
        'count': 200
    }

    response = requests.get(url, params=params, headers=HEADERS).json()

    print(response['response']['total_count'])


all_dates()
