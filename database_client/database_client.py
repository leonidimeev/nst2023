import json
import psycopg2
from sqlite3 import OperationalError
from telegram_bot.config import database_name, database_host, database_port
from telegram_bot.config import DATABASE_USER, DATABASE_PASSWORD


def check_database():
    try:
        conn = psycopg2.connect(database=database_name, user=DATABASE_USER, password=DATABASE_PASSWORD,
                                host=database_host, port=database_port)
        cursor = conn.cursor()

        # Define the table names and column names to check
        table_column_checks = {
            'logs': ['telegram_id', 'request', 'response'],
            'users': ['id', 'added_to_attachment_menu', 'can_join_groups', 'can_read_all_group_messages',
                      'first_name', 'full_name', 'is_bot', 'is_premium', 'language_code',
                      'last_name', 'link', 'name', 'supports_inline_queries', 'username'],
            'chats': ['id', 'name', 'user_id', 'log_ids'],
            'chat_pointer': ['user_id', 'chat_id']
        }

        for table, columns in table_column_checks.items():
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'")
            existing_columns = [row[0] for row in cursor.fetchall()]

            if all(column in existing_columns for column in columns):
                print(f"Table '{table}' exists with all required columns.")
            else:
                print(f"Table '{table}' is missing some columns.")

        cursor.close()
        conn.close()
        return True
    except OperationalError:
        return False


#region Logs
def get_log(log_id):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(database=database_name, user=DATABASE_USER, password=DATABASE_PASSWORD,
                            host=database_host, port=database_port)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute SELECT statement to fetch the chat by chat_id
    cur.execute("SELECT * FROM logs WHERE id = %s", (log_id))
    row = cur.fetchone()

    # Close database connection and cursor
    cur.close()
    conn.close()

    return row


def insert_log(telegram_id, request, response):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(database=database_name, user=DATABASE_USER, password=DATABASE_PASSWORD, host=database_host,
                            port=database_port)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute INSERT statement with placeholders
    cur.execute("INSERT INTO logs (telegram_id, request, response) VALUES (%s, %s, %s)",
                (telegram_id, request, json.dumps(response)))

    # Commit changes to the database
    conn.commit()

    # Close database connection and cursor
    cur.close()
    conn.close()
#endregion


#region Users
def insert_user(user):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(database=database_name, user=DATABASE_USER, password=DATABASE_PASSWORD, host=database_host,
                            port=database_port)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute INSERT statement with placeholders
    cur.execute(
        "INSERT INTO users (id, added_to_attachment_menu, can_join_groups, can_read_all_group_messages, first_name, "
        "full_name, is_bot, is_premium, last_name, link, name, supports_inline_queries, username) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (user.id, user.added_to_attachment_menu, user.can_join_groups, user.can_read_all_group_messages,
         user.first_name, user.full_name, user.is_bot, user.is_premium, user.last_name, user.link,
         user.name, user.supports_inline_queries, user.username))

    # Commit changes to the database
    conn.commit()

    # Close database connection and cursor
    cur.close()
    conn.close()


def delete_user(user_id):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(database=database_name, user=DATABASE_USER, password=DATABASE_PASSWORD, host=database_host,
                            port=database_port)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute DELETE statement with a WHERE clause to delete the user by ID
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))

    # Commit changes to the database
    conn.commit()

    # Close database connection and cursor
    cur.close()
    conn.close()


def is_user_exists(user_id):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(database=database_name, user=DATABASE_USER, password=DATABASE_PASSWORD, host=database_host,
                            port=database_port)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute SELECT statement with a WHERE clause to check if the user exists
    cur.execute("SELECT EXISTS(SELECT 1 FROM users WHERE id = %s)", (user_id,))
    result = cur.fetchone()[0]

    # Close database connection and cursor
    cur.close()
    conn.close()

    return result
#endregion


#region Chats
def create_chat(name, user_id, log_ids):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(database=database_name, user=DATABASE_USER, password=DATABASE_PASSWORD,
                            host=database_host, port=database_port)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute INSERT statement with placeholders
    cur.execute("INSERT INTO chats (name, user_id, log_ids) VALUES (%s, %s, %s) RETURNING *",
                (name, user_id, log_ids))

    # Fetch the inserted chat
    inserted_chat = cur.fetchone()

    # Commit changes to the database
    conn.commit()

    # Close database connection and cursor
    cur.close()
    conn.close()

    # Return the inserted chat
    return inserted_chat


def update_chat(chat_id, name, user_id, log_ids):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(database=database_name, user=DATABASE_USER, password=DATABASE_PASSWORD,
                            host=database_host, port=database_port)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute UPDATE statement to update the chat
    cur.execute("UPDATE chats SET name = %s, user_id = %s, log_ids = %s WHERE id = %s",
                (name, user_id, log_ids, chat_id))

    # Commit changes to the database
    conn.commit()

    # Close database connection and cursor
    cur.close()
    conn.close()


def get_chat(chat_id):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(database=database_name, user=DATABASE_USER, password=DATABASE_PASSWORD,
                            host=database_host, port=database_port)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute SELECT statement to fetch the chat by chat_id
    cur.execute("SELECT * FROM chats WHERE id = %s", (chat_id,))
    row = cur.fetchone()

    # Close database connection and cursor
    cur.close()
    conn.close()

    return row


def get_chats(user_id):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(database=database_name, user=DATABASE_USER, password=DATABASE_PASSWORD,
                            host=database_host, port=database_port)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute SELECT statement to fetch chats for the given user_id
    cur.execute("SELECT * FROM chats WHERE user_id = %s", (user_id,))
    rows = cur.fetchall()

    # Close database connection and cursor
    cur.close()
    conn.close()

    return rows


def delete_chat(chat_id):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(database=database_name, user=DATABASE_USER, password=DATABASE_PASSWORD,
                            host=database_host, port=database_port)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute DELETE statement with a WHERE clause to delete the chat by chat_id
    cur.execute("DELETE FROM chats WHERE id = %s", (chat_id,))

    # Commit changes to the database
    conn.commit()

    # Close database connection and cursor
    cur.close()
    conn.close()
#endregion


#region ChatPointers
def delete_chat_pointer(user_id, chat_id):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(database=database_name, user=DATABASE_USER, password=DATABASE_PASSWORD,
                            host=database_host, port=database_port)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute DELETE statement with a WHERE clause to delete the chat pointer by user_id and chat_id
    cur.execute("DELETE FROM chat_pointer WHERE user_id = %s AND chat_id = %s", (user_id, chat_id))

    # Commit changes to the database
    conn.commit()

    # Close database connection and cursor
    cur.close()
    conn.close()


def get_chat_pointer(user_id):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(database=database_name, user=DATABASE_USER, password=DATABASE_PASSWORD,
                            host=database_host, port=database_port)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute SELECT statement to fetch the chat pointer by user_id and chat_id

    cur.execute("SELECT * FROM chat_pointer WHERE user_id = %s", (user_id,))
    row = cur.fetchone()

    # Close database connection and cursor
    cur.close()
    conn.close()

    return row


def update_chat_pointer(user_id, chat_id):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(database=database_name, user=DATABASE_USER, password=DATABASE_PASSWORD,
                            host=database_host, port=database_port)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute UPDATE statement to update the chat pointer
    cur.execute("UPDATE chat_pointer SET chat_id = %s WHERE user_id = %s", (chat_id, user_id))

    # Commit changes to the database
    conn.commit()

    # Close database connection and cursor
    cur.close()
    conn.close()


def create_chat_pointer(user_id, chat_id):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(database=database_name, user=DATABASE_USER, password=DATABASE_PASSWORD,
                            host=database_host, port=database_port)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute INSERT statement with placeholders
    cur.execute("INSERT INTO chat_pointer (user_id, chat_id) VALUES (%s, %s) RETURNING *",
                (user_id, chat_id))

    # Fetch the inserted chat pointer
    inserted_chat_pointer = cur.fetchone()

    # Commit changes to the database
    conn.commit()

    # Close database connection and cursor
    cur.close()
    conn.close()

    # Return the inserted chat pointer
    return inserted_chat_pointer
#endregion
