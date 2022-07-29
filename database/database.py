from sqlite3 import connect
from sqlite3.dbapi2 import Cursor

DB_NAME = "C:\\Maki\\Python code\\Courses\\sakura\\database\\user_records.db"

# create database inside database folder if not exists
connection = connect(DB_NAME, check_same_thread=False)

cursor = connection.cursor()


def create_table():
    """function to create table inside database"""
    # create table user inside database if not exists
    table_script = '''CREATE TABLE IF NOT EXISTS User(
                    id INT,
                    last_name VARCHAR(255),
                    first_name VARCHAR(255),
                    phone VARCHAR(150),
                    sex VARCHAR(10)
                );
                '''
    cursor.executescript(table_script)
    connection.commit()


def insert_record(id, last_name, first_name, phone, sex):
    """function to insert record inside table"""
    cursor.execute("INSERT INTO User(id, last_name, first_name, phone, sex) VALUES(?, ?, ?, ?, ?)",
                   (id, last_name, first_name, phone, sex))
    connection.commit()


def update_all_record(id, last_name, first_name, phone, sex):
    cursor.execute(
        f"UPDATE User SET last_name='{last_name}', first_name='{first_name}', phone='{phone}', sex='{sex}' WHERE id={id}"
    )
    connection.commit()


def update_one_record(id, column, value):
    cursor.execute(
        f"UPDATE User SET {column}='{value}' WHERE id={id}"
    )
    connection.commit()


def find_all():
    data = cursor.execute("SELECT * FROM User")
    return data


def delete_record(id):
    cursor.execute(f"DELETE FROM User WHERE id={id}")
    connection.commit()


def get_user_by_id(id):
    data = cursor.execute(f"SELECT * FROM User WHERE id={id}")
    return data
