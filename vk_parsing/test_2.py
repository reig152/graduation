import requests
import time
import datetime
import string
import re

# ключ доступа API
ACCESS_TOKEN = ''

# заголовки для запроса
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}


class GetPostsComments:
    """
    Класс, отвечающий за поиск записей по запросу
    и выгрузке комментариев из найденных постов.
    """
    def get_response(self, params, api_method):
        """Метод, вызывающий запрос к API."""

        url = f'https://api.vk.com/method/{api_method}'

        response = requests.get(url, params=params, headers=HEADERS)

        return response.json()

    def all_dates(self):
        """Метод генерирует время для поискового запроса."""
        end_date = datetime.datetime.today().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        start_date = end_date - datetime.timedelta(days=365)

        delta = datetime.timedelta(hours=2)

        while end_date > start_date:
            start_time = int((end_date - delta).timestamp())
            end_time = int(end_date.timestamp())
            # print(start_time, end_time)
            self.get_posts_ids(start_time, end_time)
            end_date -= delta
            time.sleep(10)

    def get_posts_ids(self, start_time, end_time):
        """Метод собирает все посты по заданному запросу."""
        try:
            params = {
                'v': '5.131',
                'q': 'Вкусно - и точка',
                'start_time': start_time,
                'end_time': end_time,
                'count': 200
            }

            api_method = 'newsfeed.search'

            response = self.get_response(params, api_method)
            data = response['response']['items']
            for i in data:
                try:
                    # если у поста 0 комментов, то не берем в выборку
                    if i['comments']['count'] > 0:
                        owner_id = i['from_id']
                        post_id = i['id']
                        text = i['text']

                        # Удаляем знаки препинания и пробелы
                        text = "".join(
                            [char for char in text if char not in string.punctuation and char != " "]
                        )
                        text = text.lower()

                        # берем только те посты, где упоминается бренд
                        filt = re.findall(r"вкусноиточка", text)
                        if filt:
                            print(f"TEXT: {i['text']}")
                            self.get_comments(owner_id, post_id)

                except KeyError as ex:
                    print(f'Что-то не так! {ex}')
        except KeyError as ex:
            print(f'Что-то не так! {ex}')

    def get_comments(self, owner_id, post_id):
        """Метод получает комментарии поста"""
        params = {
            'v': '5.131',
            'post_id': post_id,
            'owner_id': owner_id
        }

        api_method = 'wall.getComments'
        response = self.get_response(params, api_method)
        data = response['response']['items']
        for comment in data:
            # тут будет запись построчно в БД, спросить в какую
            # и что кроме текста надо ещё
            print(f"COMMENT: {comment['text']}\n\n")

    def add_to_db(self):
        """Метод добавляет комментарии в БД."""
        # надо подумать что туда закидывать
        # точно дату, комменты, возможно текст самого поста ещё


def main():
    """Модуль запуска скрипта."""
    g = GetPostsComments()
    g.all_dates()


if __name__ == '__main__':
    main()
