import sqlite3
from config import DbFile

def openDb():
    """เปิดการเชื่อมต่อฐานข้อมูล SQLite และตั้งค่า row ให้เรียกเป็นชื่อคอลัมน์ได้"""
    conn = sqlite3.connect(DbFile)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
