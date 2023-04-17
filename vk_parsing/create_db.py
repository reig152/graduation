import sqlite3 as sq


def main():
    with sq.connect('comments.db') as con:
        cur = con.cursor()
        cur.execute("""
        CREATE TABLE comments (
          company TEXT,
          owner_id INT,
          post_id INT,
          date INT,
          text TEXT
        )
      """)


if __name__ == '__main__':
    main()
