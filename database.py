import mysql.connector
from config import DB_CONFIG
from datetime import datetime


def create_tables():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Таблица пользователей бота
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username VARCHAR(255),
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Таблица дней рождений
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS birthdays (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT,
            full_name VARCHAR(255) NOT NULL,
            birthdate DATE NOT NULL,
            contact_info TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


def add_user(user_id, username, first_name, last_name):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT IGNORE INTO users (user_id, username, first_name, last_name) VALUES (%s, %s, %s, %s)",
        (user_id, username, first_name, last_name)
    )
    conn.commit()
    cursor.close()
    conn.close()


def add_birthday(user_id, full_name, birthdate, contact_info):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO birthdays (user_id, full_name, birthdate, contact_info) VALUES (%s, %s, %s, %s)",
        (user_id, full_name, birthdate, contact_info)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_birthdays_by_user(user_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, full_name, birthdate, contact_info FROM birthdays WHERE user_id = %s",
        (user_id,)
    )
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def delete_birthday(birthday_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM birthdays WHERE id = %s", (birthday_id,))
    conn.commit()
    cursor.close()
    conn.close()


def get_all_birthdays():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.user_id, b.full_name, b.birthdate, b.contact_info, u.first_name AS user_first_name
        FROM birthdays b
        JOIN users u ON b.user_id = u.user_id
    """)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result
