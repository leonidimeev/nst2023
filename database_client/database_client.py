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
                      'last_name', 'link', 'name', 'supports_inline_queries', 'username']
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