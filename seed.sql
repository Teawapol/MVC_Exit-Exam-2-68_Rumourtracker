-- Users (อย่างน้อย 10 คน)
INSERT INTO Users (userId, name, role) VALUES
(1,'Aom','user'),
(2,'Beam','user'),
(3,'Chat','user'),
(4,'Dom','user'),
(5,'Eve','user'),
(6,'Fah','user'),
(7,'Game','user'),
(8,'Hana','user'),
(9,'Ice','checker'),
(10,'Jin','checker');

-- Rumour (อย่างน้อย 8 ข่าว, รหัส 8 หลักตัวแรกไม่ใช่ 0)
INSERT INTO Rumour (rumourId, title, source, createdAt, credibility, status, verdict, checkedAt) VALUES
('12345678','น้ำดื่มยี่ห้อดังปนเปื้อนสารพิษ','โพสต์บน Facebook','2026-02-07',35,'normal','unknown',NULL),
('23456789','ปิดห้างทุกแห่งวันพรุ่งนี้เพราะเหตุฉุกเฉิน','ไลน์กลุ่ม','2026-02-07',20,'normal','unknown',NULL),
('34567891','โรงเรียนจะเลื่อนเปิดเทอมแบบกะทันหัน','ทวิตเตอร์','2026-02-07',55,'normal','unknown',NULL),
('45678912','มีการแจกเงินสดหน้าสถานีรถไฟฟ้า','TikTok','2026-02-07',25,'normal','unknown',NULL),
('56789123','พบแผ่นดินไหวใหญ่คืนนี้แน่นอน','เพจข่าวลือ','2026-02-07',10,'normal','unknown',NULL),
('67891234','มีวัคซีนล็อตใหม่เข้า รพ. ฟรี','ข่าวแชร์ต่อ','2026-02-07',60,'normal','unknown',NULL),
('78912345','อินเทอร์เน็ตจะดับทั้งประเทศ 3 วัน','โพสต์ในฟอรั่ม','2026-02-07',15,'normal','unknown',NULL),
('89123456','รถเมล์สายหลักหยุดให้บริการถาวร','ข่าวลือในชุมชน','2026-02-07',45,'normal','unknown',NULL);
