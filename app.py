import os
import webbrowser
from threading import Timer
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_secret_key_for_my_app" 

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, fullname TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, title TEXT NOT NULL, task_date TEXT NOT NULL, task_type TEXT NOT NULL, FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    # ترقية المهام القديمة بصمت
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN task_time TEXT DEFAULT ''")
        cursor.execute("ALTER TABLE tasks ADD COLUMN duration TEXT DEFAULT ''")
    except: pass
    
    try:
        # إضافة عمود "حالة المهمة" للتمييز بين المنجز والغير منجز
        cursor.execute("ALTER TABLE tasks ADD COLUMN status TEXT DEFAULT 'قيد التنفيذ'")
    except: pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, day TEXT NOT NULL, subject TEXT NOT NULL, class_time TEXT NOT NULL, FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, subject TEXT NOT NULL, exam_date TEXT NOT NULL, exam_time TEXT NOT NULL, FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    if "user_id" not in session: return redirect(url_for("login"))
    return render_template("home.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password")
        if password != request.form.get("confirmpassword"): return render_template("signup.html", error="كلمات المرور غير متطابقة")
        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)", (fullname, email, generate_password_hash(password)))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except: return render_template("signup.html", error="الإيميل مستخدم مسبقاً")
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, fullname, password FROM users WHERE email = ?", (request.form.get("email"),))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[2], request.form.get("password")):
            session["user_id"] = user[0]
            session["fullname"] = user[1]
            return redirect(url_for("home"))
        return render_template("login.html", error="بيانات الدخول غير صحيحة")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/schedule", methods=["GET", "POST"])
def schedule():
    if "user_id" not in session: return redirect(url_for("login"))
    user_id = session["user_id"]
    if request.method == "POST":
        conn = sqlite3.connect("users.db")
        conn.execute("INSERT INTO schedule (user_id, day, subject, class_time) VALUES (?, ?, ?, ?)", (user_id, request.form.get("day"), request.form.get("subject"), request.form.get("class_time")))
        conn.commit()
        conn.close()
        return redirect(url_for("schedule"))
    conn = sqlite3.connect("users.db")
    schedule_items = conn.execute("SELECT id, day, subject, class_time FROM schedule WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return render_template("schedule.html", schedule_items=schedule_items)

@app.route("/delete_schedule/<int:item_id>", methods=["POST"])
def delete_schedule(item_id):
    if "user_id" not in session: return redirect(url_for("login"))
    conn = sqlite3.connect("users.db")
    conn.execute("DELETE FROM schedule WHERE id = ? AND user_id = ?", (item_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("schedule"))

@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    if "user_id" not in session: return redirect(url_for("login"))
    user_id = session["user_id"]
    conn = sqlite3.connect("users.db")
    if request.method == "POST":
        conn.execute("INSERT INTO tasks (user_id, title, task_date, task_time, duration, task_type) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, request.form.get("title"), request.form.get("task_date"), request.form.get("task_time"), request.form.get("duration"), request.form.get("task_type")))
        conn.commit()
        conn.close()
        return redirect(url_for("tasks"))
    task_items = conn.execute("SELECT id, title, task_date, task_time, duration, task_type, status FROM tasks WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return render_template("tasks.html", task_items=task_items)

# مسار إنجاز المهمة
@app.route("/complete_task/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    if "user_id" not in session: return redirect(url_for("login"))
    conn = sqlite3.connect("users.db")
    conn.execute("UPDATE tasks SET status='منجزة' WHERE id=? AND user_id=?", (task_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("tasks"))

@app.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    if "user_id" not in session: return redirect(url_for("login"))
    user_id = session["user_id"]
    conn = sqlite3.connect("users.db")
    if request.method == "POST":
        conn.execute("UPDATE tasks SET title=?, task_date=?, task_time=?, duration=?, task_type=? WHERE id=? AND user_id=?", 
                     (request.form.get("title"), request.form.get("task_date"), request.form.get("task_time"), request.form.get("duration"), request.form.get("task_type"), task_id, user_id))
        conn.commit()
        conn.close()
        return redirect(url_for("tasks"))
    task = conn.execute("SELECT id, title, task_date, task_time, duration, task_type FROM tasks WHERE id=? AND user_id=?", (task_id, user_id)).fetchone()
    conn.close()
    return render_template("edit_task.html", task=task)

@app.route("/delete_task/<int:item_id>", methods=["POST"])
def delete_task(item_id):
    if "user_id" not in session: return redirect(url_for("login"))
    conn = sqlite3.connect("users.db")
    conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (item_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("tasks"))

@app.route("/exam", methods=["GET", "POST"])
def exam():
    if "user_id" not in session: return redirect(url_for("login"))
    user_id = session["user_id"]
    conn = sqlite3.connect("users.db")
    if request.method == "POST":
        conn.execute("INSERT INTO exams (user_id, subject, exam_date, exam_time) VALUES (?, ?, ?, ?)", (user_id, request.form.get("subject"), request.form.get("exam_date"), request.form.get("exam_time")))
        conn.commit()
        conn.close()
        return redirect(url_for("exam"))
    exam_items = conn.execute("SELECT id, subject, exam_date, exam_time FROM exams WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return render_template("exam.html", exam_items=exam_items)

@app.route("/delete_exam/<int:item_id>", methods=["POST"])
def delete_exam(item_id):
    if "user_id" not in session: return redirect(url_for("login"))
    conn = sqlite3.connect("users.db")
    conn.execute("DELETE FROM exams WHERE id = ? AND user_id = ?", (item_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("exam"))

@app.route("/bermuda")
def bermuda():
    if "user_id" not in session: return redirect(url_for("login"))
    return render_template("bermuda.html")

# --------- مسار لوحة الإحصائيات (الداشبورد) ---------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session: return redirect(url_for("login"))
    user_id = session["user_id"]
    conn = sqlite3.connect("users.db")
    
    total_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE user_id=?", (user_id,)).fetchone()[0]
    completed_tasks = conn.execute("SELECT duration FROM tasks WHERE user_id=? AND status='منجزة'", (user_id,)).fetchall()
    total_exams = conn.execute("SELECT COUNT(*) FROM exams WHERE user_id=?", (user_id,)).fetchone()[0]
    conn.close()

    completed_count = len(completed_tasks)
    total_hours = 0
    for task in completed_tasks:
        try:
            total_hours += float(task[0]) # نجمع الساعات إذا كانت أرقاماً
        except (ValueError, TypeError):
            pass

    return render_template("dashboard.html", fullname=session.get("fullname"), total_tasks=total_tasks, completed_count=completed_count, total_hours=total_hours, total_exams=total_exams)

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        Timer(1, lambda: webbrowser.open("http://127.0.0.1:5000/login")).start()
    app.run(debug=True)