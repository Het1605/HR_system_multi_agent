# db/database.py
# This file handles ALL database operations for the HR system.
# Uses SQLite only.
# NO business logic, NO AI logic.

import sqlite3
from pathlib import Path

# --------------------------------------------------
# Database connection
# --------------------------------------------------

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

    # Attendance table (HR-assigned working hours)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
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
    Insert a new employee.
    Returns employee_id.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO employees (name, email, department)
        VALUES (?, ?, ?)
    """, (name, email, department.upper()))

    conn.commit()
    employee_id = cursor.lastrowid
    conn.close()

    return employee_id


def employee_exists(email):
    """
    Check if an employee exists using email.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 FROM employees WHERE email = ?
    """, (email,))

    exists = cursor.fetchone() is not None
    conn.close()

    return exists


def get_employee_by_id(employee_id):
    """
    Fetch employee by ID.
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

    if not row:
        return None

    return {
        "employee_id": row[0],
        "name": row[1],
        "email": row[2],
        "department": row[3]
    }


def get_employee_by_name(name):
    """
    Fetch employees by name.
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

    return [
        {
            "employee_id": r[0],
            "name": r[1],
            "email": r[2],
            "department": r[3]
        }
        for r in rows
    ]


# --------------------------------------------------
# Attendance-related DB functions (HR-driven)
# --------------------------------------------------

def attendance_exists(employee_id, date):
    """
    Check if attendance already exists for employee on a date.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 FROM attendance
        WHERE employee_id = ? AND date = ?
    """, (employee_id, date))

    exists = cursor.fetchone() is not None
    conn.close()

    return exists


def assign_working_hours(employee_id, date, start_time, end_time):
    """
    Assign working hours for an employee on a given date.
    One record per employee per date.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO attendance (employee_id, date, start_time, end_time)
        VALUES (?, ?, ?, ?)
    """, (employee_id, date, start_time, end_time))

    conn.commit()
    conn.close()


def get_working_hours(employee_id, date):
    """
    Get working hours for an employee on a specific date.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT start_time, end_time
        FROM attendance
        WHERE employee_id = ? AND date = ?
    """, (employee_id, date))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "start_time": row[0],
        "end_time": row[1]
    }


# --------------------------------------------------
# Initialize DB
# --------------------------------------------------

create_tables()