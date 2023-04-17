import requests
from math import ceil
import logging
from logging.handlers import RotatingFileHandler
from add_to_db import AddToDb

# Здесь задана глобальная конфигурация для всех логгеров
logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

# А тут установлены настройки логгера для текущего файла - example_for_log.py
logger = logging.getLogger(__name__)
# Устанавливаем уровень, с которого логи будут сохраняться в файл
logger.setLevel(logging.INFO)
# Указываем обработчик логов
handler = RotatingFileHandler(
    'my_logger.log',
    maxBytes=50000000,
    backupCount=5
)
logger.addHandler(handler)

# Указываем обработчик логов для файла program.log
handler2 = RotatingFileHandler(
    'program.log',
    maxBytes=50000000,
    backupCount=5
)
logging.getLogger().addHandler(handler2)


# ключ доступа API
ACCESS_TOKEN = ''

# заголовки для запроса
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}

GROUP_DOMAINS = {
    'vkusnoitochka': 'vkusno_itochka',
    'starscofee': 'starscoffee_official',
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

    def get_posts_ids(self, domain):
        """Получение id постов."""
        pagen = self.pagen()
        post_ids = []
        try:
            for x in range(pagen):
                offset = x * 100
                params = {
                    'domain': domain,
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

        except Exception as ex:
            logger.error(f'Возникла непредвиденная ошибка в сборе id! {ex}')

    def get_comments(self):
        """Метод получает комментарии поста."""
        for comp, domain in GROUP_DOMAINS.items():
            source = self.get_posts_ids(domain)
            post_ids = source[0]
            owner_id = source[-1]
            for id in post_ids:
                try:
                    params = {
                        'v': '5.131',
                        'post_id': id,
                        'owner_id': owner_id
                    }

                    api_method = 'wall.getComments'
                    response = self.get_response(params, api_method)
                    data = response['response']['items']
                    stats = {}
                    for comment in data:
                        # тут будет запись построчно в БД, спросить в какую
                        # и что кроме текста надо ещё
                        stats['company'] = comp
                        stats['owner_id'] = owner_id
                        stats['post_id'] = id
                        stats['date'] = comment['date']
                        stats['text'] = comment['text']

                        a = AddToDb()
                        a.add_to_db(stats)

                except Exception as ex:
                    logger.error(
                        f'Возникла непредвиденная ошибка в получении '
                        f'комментариев! {ex}'
                    )


def main():
    """Модуль запуска скрипта."""
    g = GetGroupComments()
    g.get_comments()


if __name__ == '__main__':
    main()
