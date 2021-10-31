import sqlite3
import datetime

def _login():
    connection = sqlite3.connect("absent.db")
    return connection


def fill_users_table(users):
    conn = _login()
    cursor = conn.cursor()
    for user in users:
        query = f'''insert or ignore into users (name, last_seen) 
            values ('{user['name']}', '{str(user['last_seen'])}')
            
            '''
        print('Query:', query)
        cursor.execute(query)
        conn.commit()
    cursor.close()


def update_last_seen(user):
    conn = _login()
    cursor = conn.cursor()
    query = f'''UPDATE users
    SET last_seen = '{str(user['last_seen'])}'
    WHERE name = '{user['name']}'
    '''
    cursor.execute(query)
    conn.commit()
    cursor.close()


def get_users():
    conn = _login()
    cursor = conn.cursor()
    query = 'select * from users'
    cursor.execute(query)
    users = []
    for row in cursor.fetchall():
        user = {
            'name' : row[0],
            'last_seen' : row[1]
        }
        users.append(user)
    cursor.close()
    return users


def on_login():
    conn = _login()
    cursor = conn.cursor()
    create_table_users_query = '''CREATE TABLE IF NOT EXISTS users (
    name TEXT NOT NULL UNIQUE,
    last_seen timestamp
    )
    '''
    cursor.execute(create_table_users_query)

    cursor.close()
