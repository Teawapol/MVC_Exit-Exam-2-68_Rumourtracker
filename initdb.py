from database import openDb
from config import PanicLimit
from datetime import datetime

def createTables(conn):
    # สร้างตารางหลัก 3 ตาราง: Users, Rumour, Report
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS Users (
            userId INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user','checker'))
        );

        CREATE TABLE IF NOT EXISTS Rumour (
            rumourId TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            source TEXT NOT NULL,
            createdAt TEXT NOT NULL,
            credibility REAL NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('normal','panic')),
            verdict TEXT NOT NULL CHECK(verdict IN ('unknown','true','false')),
            checkedAt TEXT
        );

        CREATE TABLE IF NOT EXISTS Report (
            reportId INTEGER PRIMARY KEY AUTOINCREMENT,
            reporterId INTEGER NOT NULL,
            rumourId TEXT NOT NULL,
            reportedAt TEXT NOT NULL,
            reportType TEXT NOT NULL CHECK(reportType IN ('distortion','incite','fake')),
            note TEXT,
            UNIQUE(reporterId, rumourId),
            FOREIGN KEY(reporterId) REFERENCES Users(userId),
            FOREIGN KEY(rumourId) REFERENCES Rumour(rumourId)
        );
        """
    )

def hasData(conn, tableName):
    cur = conn.execute(f"SELECT COUNT(*) AS c FROM {tableName}")
    return cur.fetchone()["c"] > 0

def seedUsers(conn):
    # Users อย่างน้อย 10 คน (มีทั้ง user และ checker)
    users = [
        (1, "Aom", "user"),
        (2, "Beam", "user"),
        (3, "Chat", "user"),
        (4, "Dom", "user"),
        (5, "Eve", "user"),
        (6, "Fah", "user"),
        (7, "Game", "user"),
        (8, "Hana", "user"),
        (9, "Ice", "checker"),
        (10, "Jin", "checker"),
    ]
    conn.executemany(
        "INSERT INTO Users (userId, name, role) VALUES (?, ?, ?)",
        users
    )

def seedRumours(conn):
    # Rumour อย่างน้อย 8 ข่าว (รหัส 8 หลัก ตัวแรกไม่ใช่ 0)
    today = datetime.now().date().isoformat()
    rumours = [
        ("12345678", "น้ำดื่มยี่ห้อดังปนเปื้อนสารพิษ", "โพสต์บน Facebook", today, 35.0, "normal", "unknown", None),
        ("23456789", "ปิดห้างทุกแห่งวันพรุ่งนี้เพราะเหตุฉุกเฉิน", "ไลน์กลุ่ม", today, 20.0, "normal", "unknown", None),
        ("34567891", "โรงเรียนจะเลื่อนเปิดเทอมแบบกะทันหัน", "ทวิตเตอร์", today, 55.0, "normal", "unknown", None),
        ("45678912", "มีการแจกเงินสดหน้าสถานีรถไฟฟ้า", "TikTok", today, 25.0, "normal", "unknown", None),
        ("56789123", "พบแผ่นดินไหวใหญ่คืนนี้แน่นอน", "เพจข่าวลือ", today, 10.0, "normal", "unknown", None),
        ("67891234", "มีวัคซีนล็อตใหม่เข้า รพ. ฟรี", "ข่าวแชร์ต่อ", today, 60.0, "normal", "unknown", None),
        ("78912345", "อินเทอร์เน็ตจะดับทั้งประเทศ 3 วัน", "โพสต์ในฟอรั่ม", today, 15.0, "normal", "unknown", None),
        ("89123456", "รถเมล์สายหลักหยุดให้บริการถาวร", "ข่าวลือในชุมชน", today, 45.0, "normal", "unknown", None),
    ]
    conn.executemany(
        """
        INSERT INTO Rumour
        (rumourId, title, source, createdAt, credibility, status, verdict, checkedAt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rumours
    )

def seedReports(conn):
    # ใส่รายงานตัวอย่าง (ต้องมีทั้ง panic และไม่ panic)
    nowText = datetime.now().isoformat(timespec="seconds")
    reports = [
        # ทำให้ข่าว 12345678 เข้าสู่ panic (มากกว่า PanicLimit=3 => ต้องมีอย่างน้อย 4 รายงาน)
        (1, "12345678", nowText, "fake", "เห็นแชร์หลายรอบ"),
        (2, "12345678", nowText, "fake", "ดูไม่น่าเชื่อถือ"),
        (3, "12345678", nowText, "distortion", "ข้อมูลไม่ครบ"),
        (4, "12345678", nowText, "incite", "ทำให้คนตื่นตระหนก"),
        (5, "12345678", nowText, "fake", "ไม่มีแหล่งอ้างอิง"),

        # ข่าว 56789123 panic เช่นกัน
        (6, "56789123", nowText, "incite", "คนแห่แชร์กัน"),
        (7, "56789123", nowText, "incite", "ปลุกปั่น"),
        (8, "56789123", nowText, "fake", "ไม่มีหลักฐาน"),
        (2, "56789123", nowText, "distortion", "บิดเบือน"),
        (3, "56789123", nowText, "fake", "ข้อมูลเท็จ"),

        # ข่าวอื่นๆ รายงานน้อย ไม่ panic
        (1, "23456789", nowText, "fake", ""),
        (2, "23456789", nowText, "fake", ""),
        (3, "34567891", nowText, "distortion", ""),
        (4, "45678912", nowText, "distortion", ""),
    ]
    conn.executemany(
        """
        INSERT OR IGNORE INTO Report
        (reporterId, rumourId, reportedAt, reportType, note)
        VALUES (?, ?, ?, ?, ?)
        """,
        reports
    )

def updateStatuses(conn):
    # อัปเดตสถานะตามจำนวนรายงานของแต่ละข่าว
    cur = conn.execute("SELECT rumourId FROM Rumour")
    for row in cur.fetchall():
        rid = row["rumourId"]
        c = conn.execute(
            "SELECT COUNT(*) AS c FROM Report WHERE rumourId = ?",
            (rid,)
        ).fetchone()["c"]

        status = "panic" if c > PanicLimit else "normal"
        conn.execute(
            "UPDATE Rumour SET status = ? WHERE rumourId = ?",
            (status, rid)
        )

def seedVerdicts(conn):
    # ตั้งผลตรวจสอบให้มีทั้ง “จริง” และ “เท็จ”
    nowText = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        "UPDATE Rumour SET verdict = 'false', checkedAt = ? WHERE rumourId = ?",
        (nowText, "23456789")
    )
    conn.execute(
        "UPDATE Rumour SET verdict = 'true', checkedAt = ? WHERE rumourId = ?",
        (nowText, "67891234")
    )

def main():
    conn = openDb()
    try:
        createTables(conn)
        conn.commit()

        if not hasData(conn, "Users"):
            seedUsers(conn)
        if not hasData(conn, "Rumour"):
            seedRumours(conn)
        if not hasData(conn, "Report"):
            seedReports(conn)

        updateStatuses(conn)
        seedVerdicts(conn)

        conn.commit()
        print("สร้างฐานข้อมูลและใส่ข้อมูลตัวอย่างเรียบร้อย")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
