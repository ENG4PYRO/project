import os
import webbrowser
from threading import Timer
from flask import Flask

from db import init_db

from routes.auth import auth_bp
from routes.main import main_bp
from routes.tasks import tasks_bp
from routes.schedule import schedule_bp
from routes.exams import exams_bp

app = Flask(__name__)
app.secret_key = "super_secret_key_for_my_app" 

init_db()


app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(schedule_bp)
app.register_blueprint(exams_bp)

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        Timer(1, lambda: webbrowser.open("http://127.0.0.1:5000/login")).start()
    app.run(debug=True)