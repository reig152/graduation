import requests
from math import ceil
import time

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

    def pagen(self):
        """Метод получает следующую страницу выдачи"""
        params = {
            'v': '5.131',
            'q': 'Вкусно - и точка',
            'count': '1'
        }

        api_method = 'newsfeed.search'

        response = self.get_response(params, api_method)
        data = response['response']['total_count']
        pagen = data / 100

        # округляем в большую сторону,
        # чтобы собрать данные со всех страниц
        return ceil(pagen)

    def get_posts_ids(self):
        """Метод собирает все посты по заданному запросу."""
        pagen = self.pagen()
        for x in range(pagen):
            try:
                offset = x * 100
                params = {
                    'q': 'Вкусно - и точка',
                    'v': '5.131',
                    'offset': offset,
                }
                print(f'OFFSET: {offset}')

                api_method = 'newsfeed.search'

                response = self.get_response(params, api_method)
                data = response['response']['items']
                for i in data:
                    try:
                        # если у поста 0 комментов, то не берем в выборку
                        if i['comments']['count'] > 0:
                            owner_id = i['from_id']
                            post_id = i['id']
                            print(f"TEXT: {i['text'][:10]}")
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
            print(f"COMMENT: {comment['text']}")


def main():
    """Модуль запуска скрипта."""
    g = GetPostsComments()
    print(g.get_posts_ids())


if __name__ == '__main__':
    main()
