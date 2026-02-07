from database import openDb

def listUsers():
    """ดึงรายชื่อผู้ใช้ทั้งหมด"""
    conn = openDb()
    try:
        cur = conn.execute(
            "SELECT userId, name, role FROM Users ORDER BY userId ASC"
        )
        return cur.fetchall()
    finally:
        conn.close()

def getUserById(userId):
    """ดึงข้อมูลผู้ใช้ตามรหัส (ถ้าไม่พบจะคืนค่า None)"""
    if userId is None:
        return None

    conn = openDb()
    try:
        cur = conn.execute(
            "SELECT userId, name, role FROM Users WHERE userId = ?",
            (userId,)
        )
        return cur.fetchone()
    finally:
        conn.close()
