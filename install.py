from contextlib import closing
import sqlite3

with closing(sqlite3.connect("blinker.db")) as connection:
    with closing(connection.cursor()) as cursor:
        try:
            cursor.execute("CREATE TABLE mode (is_night BOOLEAN)")
        except sqlite3.OperationalError:
            cursor.execute("DROP TABLE mode")
            cursor.execute("CREATE TABLE mode (is_night BOOLEAN)")
        cursor.execute("INSERT INTO mode (is_night) VALUES (true)")
        connection.commit()


with closing(sqlite3.connect("blinker.db")) as connection:
    with closing(connection.cursor()) as cursor:
        values = cursor.execute("SELECT is_night FROM mode").fetchall()[0]
        assert values == (1,), "Installation fail"