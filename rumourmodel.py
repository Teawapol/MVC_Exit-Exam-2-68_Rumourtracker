from database import openDb
from config import PanicLimit
from datetime import datetime
import sqlite3

def listRumours(sortMode="reports"):
    """รายการข่าวลือทั้งหมด พร้อมจำนวนรายงาน (รายงานเยอะ = ร้อนแรง)"""
    orderSql = "reportCount DESC, createdAt DESC"
    if sortMode == "credibility":
        orderSql = "credibility DESC, createdAt DESC"
    elif sortMode == "date":
        orderSql = "createdAt DESC"

    conn = openDb()
    try:
        sql = f"""
        SELECT
            r.rumourId, r.title, r.source, r.createdAt,
            r.credibility, r.status, r.verdict, r.checkedAt,
            COUNT(p.reportId) AS reportCount
        FROM Rumour r
        LEFT JOIN Report p ON r.rumourId = p.rumourId
        GROUP BY r.rumourId
        ORDER BY {orderSql}
        """
        cur = conn.execute(sql)
        return cur.fetchall()
    finally:
        conn.close()

def getRumourWithCount(rumourId):
    """ดึงข่าวลือ 1 ข่าว พร้อมจำนวนรายงาน"""
    conn = openDb()
    try:
        cur = conn.execute(
            """
            SELECT
                r.rumourId, r.title, r.source, r.createdAt,
                r.credibility, r.status, r.verdict, r.checkedAt,
                COUNT(p.reportId) AS reportCount
            FROM Rumour r
            LEFT JOIN Report p ON r.rumourId = p.rumourId
            WHERE r.rumourId = ?
            GROUP BY r.rumourId
            """,
            (rumourId,)
        )
        return cur.fetchone()
    finally:
        conn.close()

def listReportsForRumour(rumourId):
    """รายการรายงานของข่าวลือ (แสดงชื่อผู้รายงาน)"""
    conn = openDb()
    try:
        cur = conn.execute(
            """
            SELECT
                p.reportId, p.reportedAt, p.reportType, p.note,
                u.userId, u.name
            FROM Report p
            JOIN Users u ON u.userId = p.reporterId
            WHERE p.rumourId = ?
            ORDER BY p.reportedAt DESC, p.reportId DESC
            """,
            (rumourId,)
        )
        return cur.fetchall()
    finally:
        conn.close()

def addReport(reporterId, rumourId, reportType, noteText):
    """เพิ่มรายงานตามกฎทางธุรกิจ
    - ผู้ใช้ 1 คน รายงานข่าวลือเดิมซ้ำไม่ได้ (Unique)
    - ข่าวลือที่ถูกตรวจสอบแล้ว รายงานเพิ่มไม่ได้
    - ถ้าจำนวนรายงาน > PanicLimit ให้สถานะเป็น panic
    """
    rumour = getRumourWithCount(rumourId)
    if rumour is None:
        return (False, "notfound")

    if rumour["verdict"] != "unknown":
        return (False, "checked")

    nowText = datetime.now().isoformat(timespec="seconds")

    conn = openDb()
    try:
        try:
            conn.execute(
                """
                INSERT INTO Report (reporterId, rumourId, reportedAt, reportType, note)
                VALUES (?, ?, ?, ?, ?)
                """,
                (reporterId, rumourId, nowText, reportType, noteText)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            # ซ้ำ: ผู้ใช้คนเดิมรายงานข่าวลือเดิมซ้ำไม่ได้
            return (False, "duplicate")

        # นับจำนวนรายงานล่าสุด
        cur = conn.execute(
            "SELECT COUNT(*) AS c FROM Report WHERE rumourId = ?",
            (rumourId,)
        )
        reportCount = cur.fetchone()["c"]

        newStatus = "panic" if reportCount > PanicLimit else "normal"
        conn.execute(
            "UPDATE Rumour SET status = ? WHERE rumourId = ?",
            (newStatus, rumourId)
        )
        conn.commit()

        return (True, "ok", reportCount, newStatus)
    finally:
        conn.close()

def setVerdict(rumourId, verdict):
    """ตั้งผลตรวจสอบ (true/false) และล็อกไม่ให้รายงานเพิ่ม"""
    if verdict not in ["true", "false"]:
        return False

    nowText = datetime.now().isoformat(timespec="seconds")
    conn = openDb()
    try:
        conn.execute(
            "UPDATE Rumour SET verdict = ?, checkedAt = ? WHERE rumourId = ?",
            (verdict, nowText, rumourId)
        )
        conn.commit()
        return True
    finally:
        conn.close()

def listPanicRumours():
    conn = openDb()
    try:
        cur = conn.execute(
            """
            SELECT
                r.rumourId, r.title, r.source, r.createdAt,
                r.credibility, r.status, r.verdict, r.checkedAt,
                COUNT(p.reportId) AS reportCount
            FROM Rumour r
            LEFT JOIN Report p ON r.rumourId = p.rumourId
            WHERE r.status = 'panic'
            GROUP BY r.rumourId
            ORDER BY reportCount DESC, r.createdAt DESC
            """
        )
        return cur.fetchall()
    finally:
        conn.close()

def listVerifiedRumours():
    conn = openDb()
    try:
        cur = conn.execute(
            """
            SELECT
                r.rumourId, r.title, r.source, r.createdAt,
                r.credibility, r.status, r.verdict, r.checkedAt,
                COUNT(p.reportId) AS reportCount
            FROM Rumour r
            LEFT JOIN Report p ON r.rumourId = p.rumourId
            WHERE r.verdict IN ('true','false')
            GROUP BY r.rumourId
            ORDER BY r.checkedAt DESC
            """
        )
        return cur.fetchall()
    finally:
        conn.close()
