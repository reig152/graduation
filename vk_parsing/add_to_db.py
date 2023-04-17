import sqlite3


class AddToDb:
    def add_to_db(self, stats):
        """Метод добавляет комментарии в БД."""
        with sqlite3.connect(
            '/home/reig/graduation/vk_parsing/comments.db'
        ) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO comments
                VALUES (
                    :company,
                    :owner_id,
                    :post_id,
                    :date,
                    :text
                )
            """, stats)
            connection.commit()
