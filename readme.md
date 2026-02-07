# Rumour Tracking System (MVC)

## วิธีติดตั้งและรัน
1) สร้าง venv แล้วติดตั้งแพ็กเกจ
```bash
python -m venv venv
# Windows
venv\Scripts\activate
pip install -r requirements.txt
```

2) สร้างฐานข้อมูล + ใส่ข้อมูลตัวอย่าง
```bash
python initdb.py
```

3) รันเว็บ
```bash
python main.py
```

แล้วเปิดในเบราว์เซอร์: http://127.0.0.1:5000

## หน้าจอที่มี (Views)
- หน้ารวมข่าวลือ: /rumours
- หน้ารายละเอียดข่าวลือ: /rumour/<rumourId>
- หน้าสรุปผล: /summary

## หมายเหตุงาน
- PanicLimit = 3 (จะเป็น PANIC เมื่อจำนวนรายงาน > 3)
- ผู้ใช้หนึ่งคนรายงานข่าวลือเดียวกันซ้ำไม่ได้ (Unique)
- ข่าวลือที่ถูกตรวจสอบแล้ว (ยืนยันจริง/เท็จ) รายงานเพิ่มไม่ได้
