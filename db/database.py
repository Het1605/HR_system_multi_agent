# db/database.py
# This file handles ALL database operations for the HR system.
# It uses SQLite (built-in with Python).
# Other agents will use the functions defined here.
# No business logic should be written in this file.

import sqlite3
from pathlib import Path

# --------------------------------------------------
# Database connection
# --------------------------------------------------

# Create a database file in the same folder
DB_PATH = Path(__file__).parent / "hr_system.db"


def get_connection():
    """
    Create and return a SQLite database connection.
    """
    return sqlite3.connect(DB_PATH)


# --------------------------------------------------
# Table creation
# --------------------------------------------------

def create_tables():
    """
    Create required tables if they do not already exist.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Employees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL
        )
    """)

    # Attendance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        )
    """)

    conn.commit()
    conn.close()


# --------------------------------------------------
# Employee-related DB functions
# --------------------------------------------------

def add_employee(name, email, department):
    """
    Insert a new employee into the employees table.
    Returns the new employee_id.

    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO employees (name, email, department)
        VALUES (?, ?, ?)
    """, (name, email, department))

    conn.commit()
    employee_id = cursor.lastrowid
    conn.close()

    return employee_id


def employee_exists(email):
    """
    Check if an employee already exists using email.
    Returns True or False.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 FROM employees WHERE email = ?
    """, (email,))

    result = cursor.fetchone()
    conn.close()

    return result is not None


def get_employee_by_id(employee_id):
    """
    Fetch employee details using employee_id.
    Returns a dictionary or None.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT employee_id, name, email, department
        FROM employees
        WHERE employee_id = ?
    """, (employee_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "employee_id": row[0],
            "name": row[1],
            "email": row[2],
            "department": row[3]
        }

    return None


def get_employee_by_name(name):
    """
    Fetch all employees with the given name.
    Returns a list of dictionaries.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT employee_id, name, email, department
        FROM employees
        WHERE name = ?
    """, (name,))

    rows = cursor.fetchall()
    conn.close()

    employees = []
    for row in rows:
        employees.append({
            "employee_id": row[0],
            "name": row[1],
            "email": row[2],
            "department": row[3]
        })

    return employees


# --------------------------------------------------
# Attendance-related DB functions
# --------------------------------------------------

def add_start_time(employee_id, date, start_time):
    """
    Insert start time for an employee on a given date.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO attendance (employee_id, date, start_time)
        VALUES (?, ?, ?)
    """, (employee_id, date, start_time))

    conn.commit()
    conn.close()


def add_end_time(employee_id, date, end_time):
    """
    Update end time for an employee on a given date.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE attendance
        SET end_time = ?
        WHERE employee_id = ? AND date = ?
    """, (end_time, employee_id, date))

    conn.commit()
    conn.close()


def get_attendance_for_date(employee_id, date):
    """
    Fetch attendance record for an employee on a specific date.
    Returns a dictionary or None.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT employee_id, date, start_time, end_time
        FROM attendance
        WHERE employee_id = ? AND date = ?
    """, (employee_id, date))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "employee_id": row[0],
            "date": row[1],
            "start_time": row[2],
            "end_time": row[3]
        }

    return None


# --------------------------------------------------
# Initialize DB (run once when module is loaded)
# --------------------------------------------------

create_tables()