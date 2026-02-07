from flask import request, session, flash
from flask import render_template as renderView
from flask import redirect as go
from flask import url_for as urlFor

from usermodel import listUsers

def register(app):
    @app.get("/login")
    def loginPage():
        users = listUsers()
        return renderView("login.html", users=users)

    @app.post("/login")
    def loginAction():
        userIdText = request.form.get("userId", "").strip()
        if userIdText == "":
            flash("กรุณาเลือกผู้ใช้เพื่อเข้าสู่ระบบ")
            return go(urlFor("loginPage"))

        try:
            userId = int(userIdText)
        except:
            flash("รหัสผู้ใช้ไม่ถูกต้อง")
            return go(urlFor("loginPage"))

        session["userId"] = userId
        flash("เข้าสู่ระบบเรียบร้อย")
        return go(urlFor("rumourList"))

    @app.get("/logout")
    def logoutAction():
        session.pop("userId", None)
        flash("ออกจากระบบแล้ว")
        return go(urlFor("rumourList"))
