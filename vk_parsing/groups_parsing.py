import requests
from math import ceil


# ключ доступа API
ACCESS_TOKEN = ''

# заголовки для запроса
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}


class GetGroupComments:
    """Класс-получения комментариев паблика ВК."""
    def get_response(self, params, api_method):
        """Метод, вызывающий запрос к API."""

        url = f'https://api.vk.com/method/{api_method}'

        response = requests.get(url, params=params, headers=HEADERS)

        return response.json()

    def pagen(self):
        """Метод получает количество постов."""
        params = {
            'domain': 'vkusno_itochka',
            'v': '5.131',
        }

        api_method = 'wall.get'

        response = self.get_response(params, api_method)
        data = response['response']['count']
        pagen = data / 100

        # округляем в большую сторону,
        # чтобы собрать данные со всех страниц
        return ceil(pagen)

    def get_posts_ids(self):
        """Получение id постов."""
        pagen = self.pagen()
        post_ids = []
        for x in range(pagen):
            offset = x * 100
            params = {
                'domain': 'vkusno_itochka',
                'v': '5.131',
                'offset': f'{offset}',
                'count': '100'
            }

            api_method = 'wall.get'

            response = self.get_response(params, api_method)
            data = response['response']['items']
            owner_id = data[0]['from_id']

            for id in data:
                post_ids.append(id['id'])

        return post_ids, owner_id

    def get_comments(self):
        """Метод получает комментарии поста."""
        source = self.get_posts_ids()
        post_ids = source[0]
        owner_id = source[-1]
        for id in post_ids:
            params = {
                'domain': 'vkusno_itochka',
                'v': '5.131',
                'post_id': id,
                'owner_id': owner_id
            }

            api_method = 'wall.getComments'
            response = self.get_response(params, api_method)
            data = response['response']['items']
            for comment in data:
                # тут будет запись построчно в БД, спросить в какую
                # и что кроме текста надо ещё
                print(comment['text'])


def main():
    """Модуль запуска скрипта."""
    g = GetGroupComments()
    g.get_comments()


if __name__ == '__main__':
    main()
