from flask import request, session, flash
from flask import render_template as renderView
from flask import redirect as go
from flask import url_for as urlFor

from config import PanicLimit
from usermodel import getUserById
from rumourmodel import (
    listRumours,
    getRumourWithCount,
    listReportsForRumour,
    addReport,
    setVerdict,
    listPanicRumours,
    listVerifiedRumours
)

def getCurrentUser():
    userId = session.get("userId")
    return getUserById(userId)

def isValidRumourId(rumourId):
    # รหัสข่าวลือต้องเป็นเลข 8 หลัก และตัวแรกห้ามเป็น 0
    return rumourId.isdigit() and len(rumourId) == 8 and rumourId[0] != "0"

def register(app):
    @app.get("/")
    def homeRedirect():
        return go(urlFor("rumourList"))

    @app.get("/rumours")
    def rumourList():
        sortMode = request.args.get("sort", "reports")
        rumours = listRumours(sortMode=sortMode)
        return renderView("rumourlist.html", rumours=rumours, sortMode=sortMode)

    @app.get("/rumour/<rumourId>")
    def rumourDetail(rumourId):
        if not isValidRumourId(rumourId):
            flash("รหัสข่าวลือไม่ถูกต้อง (ต้องเป็นเลข 8 หลัก และตัวแรกห้ามเป็น 0)")
            return go(urlFor("rumourList"))

        rumour = getRumourWithCount(rumourId)
        if rumour is None:
            flash("ไม่พบข่าวลือที่ต้องการ")
            return go(urlFor("rumourList"))

        reports = listReportsForRumour(rumourId)
        user = getCurrentUser()

        canReport = False
        reasonText = ""
        if user is None:
            reasonText = "ต้องเข้าสู่ระบบก่อนจึงจะรายงานได้"
        elif rumour["verdict"] != "unknown":
            reasonText = "ข่าวลือนี้ถูกตรวจสอบแล้ว จึงรายงานเพิ่มไม่ได้"
        else:
            canReport = True

        return renderView(
            "rumourdetail.html",
            rumour=rumour,
            reports=reports,
            canReport=canReport,
            reasonText=reasonText,
            panicLimit=PanicLimit
        )

    @app.post("/rumour/<rumourId>/report")
    def rumourReport(rumourId):
        if not isValidRumourId(rumourId):
            flash("รหัสข่าวลือไม่ถูกต้อง")
            return go(urlFor("rumourList"))

        user = getCurrentUser()
        if user is None:
            flash("กรุณาเข้าสู่ระบบก่อน")
            return go(urlFor("loginPage"))

        reportType = request.form.get("reportType", "").strip()
        noteText = request.form.get("note", "").strip()

        if reportType not in ["distortion", "incite", "fake"]:
            flash("ประเภทรายงานไม่ถูกต้อง")
            return go(urlFor("rumourDetail", rumourId=rumourId))

        result = addReport(user["userId"], rumourId, reportType, noteText)

        if result[0] is False:
            reason = result[1]
            if reason == "checked":
                flash("ข่าวลือนี้ถูกตรวจสอบแล้ว จึงรายงานเพิ่มไม่ได้")
            elif reason == "duplicate":
                flash("คุณเคยรายงานข่าวลือนี้แล้ว (รายงานซ้ำไม่ได้)")
            elif reason == "notfound":
                flash("ไม่พบข่าวลือที่ต้องการ")
            else:
                flash("รายงานไม่สำเร็จ")
        else:
            reportCount = result[2]
            newStatus = result[3]
            if newStatus == "panic":
                flash(f"รายงานสำเร็จ ตอนนี้มีรายงาน {reportCount} ครั้ง สถานะเปลี่ยนเป็น PANIC")
            else:
                flash(f"รายงานสำเร็จ ตอนนี้มีรายงาน {reportCount} ครั้ง")

        return go(urlFor("rumourDetail", rumourId=rumourId))

    @app.post("/rumour/<rumourId>/verify")
    def rumourVerify(rumourId):
        if not isValidRumourId(rumourId):
            flash("รหัสข่าวลือไม่ถูกต้อง")
            return go(urlFor("rumourList"))

        user = getCurrentUser()
        if user is None:
            flash("กรุณาเข้าสู่ระบบก่อน")
            return go(urlFor("loginPage"))

        if user["role"] != "checker":
            flash("ต้องเป็นผู้ตรวจสอบเท่านั้นจึงจะยืนยันผลได้")
            return go(urlFor("rumourDetail", rumourId=rumourId))

        verdict = request.form.get("verdict", "").strip()
        ok = setVerdict(rumourId, verdict)
        if ok:
            text = "ข้อมูลจริง" if verdict == "true" else "ข้อมูลเท็จ"
            flash(f"ยืนยันผลแล้ว: {text}")
        else:
            flash("ยืนยันผลไม่สำเร็จ")

        return go(urlFor("rumourDetail", rumourId=rumourId))

    @app.get("/summary")
    def summaryPage():
        panicRumours = listPanicRumours()
        verifiedRumours = listVerifiedRumours()
        return renderView(
            "summary.html",
            panicRumours=panicRumours,
            verifiedRumours=verifiedRumours,
            panicLimit=PanicLimit
        )
