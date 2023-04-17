import requests
import time
import datetime
import string
import re
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

POST_QUERIES = {
    'vkusnoitochka': 'Вкусно - и точка',
    'starscofee': 'Stars Coffee',
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
        for comp, query in POST_QUERIES.items():
            try:
                params = {
                    'v': '5.131',
                    'q': query,
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

                            # форматируем текст
                            pr_text = self.preprocess_text(text)
                            regexp = self.preprocess_text(query)

                            # берем только те посты, где упоминается бренд
                            filt = re.findall(fr"{regexp}", pr_text)
                            if filt:
                                self.get_comments(owner_id, post_id, comp)

                    except KeyError as ex:
                        logger.error(f'Ошибка с ключами! {ex}')
                    except Exception as ex:
                        logger.error(
                            f'Возникла ошибка '
                            f'в получении комментариев! {ex}'
                        )
            except Exception as ex:
                logger.error(f'Возникла ошибка в получении id! {ex}')

    def get_comments(self, owner_id, post_id, comp):
        """Метод получает комментарии поста"""
        params = {
            'v': '5.131',
            'post_id': post_id,
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
            stats['owner_id'] = comment['owner_id']
            stats['post_id'] = comment['post_id']
            stats['date'] = comment['date']
            stats['text'] = comment['text']

            a = AddToDb()
            a.add_to_db(stats)

    def preprocess_text(self, text):
        # Удаляем знаки препинания и пробелы
        text = "".join(
            char for char in text
            if char not in string.punctuation and char not in string.whitespace
        )
        # приводим текст поста в нижний регистр
        text = text.lower()
        return text


def main():
    """Модуль запуска скрипта."""
    g = GetPostsComments()
    g.all_dates()


if __name__ == '__main__':
    main()
