from flask import Flask, session
from flask import url_for as urlFor
from flask import get_flashed_messages as getFlash

from config import PanicLimit
from usermodel import getUserById
import authcontroller
import rumourcontroller

def createApp():
    app = Flask(__name__, static_folder="static", template_folder="view")
    app.secret_key = "devkey-change-me"

    # ทำให้เทมเพลตเรียก url ได้แบบไม่มีขีดล่าง (ใน view ใช้ url('endpoint'))
    app.jinja_env.globals["url"] = urlFor

    # ส่งข้อมูลที่ใช้ซ้ำบ่อยให้ทุกหน้า
    @app.context_processor
    def injectCommon():
        userId = session.get("userId")
        currentUser = getUserById(userId)
        return {
            "currentUser": currentUser,
            "messages": getFlash(),
            "panicLimit": PanicLimit
        }

    authcontroller.register(app)
    rumourcontroller.register(app)
    return app

if __name__ == "__main__":
    app = createApp()
    app.run(debug=True)
