import os
import webbrowser
from threading import Timer
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# --- (تعديل جديد 1) إعداد مفتاح سري لحماية الجلسات ---
app.secret_key = "super_secret_key_for_my_app" 

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # 1. جدول المستخدمين
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    # 2. جدول المهام
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            task_date TEXT NOT NULL,
            task_type TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # 3. جدول الجدول الدراسي
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            day TEXT NOT NULL,
            subject TEXT NOT NULL,
            class_time TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # 4. جدول الامتحانات (الجديد)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            exam_date TEXT NOT NULL,
            exam_time TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()

init_db()
# ---------------- ROUTES ----------------
@app.route("/")
def home():
    # --- (تعديل جديد 2) حماية الصفحة الرئيسية ---
    if "user_id" not in session:
        return redirect(url_for("login")) # إذا لم يسجل دخول، يرجع لصفحة الدخول
        
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmpassword = request.form.get("confirmpassword")

        if password != confirmpassword:
            return render_template("signup.html", error="كلمات المرور غير متطابقة")

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)",
                (fullname, email, hashed_password)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return render_template("signup.html", error="الإيميل مستخدم مسبقاً")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        
        # --- (تعديل جديد 3) جلبنا الـ id والاسم مع الباسورد لكي نحفظهم بالجلسة ---
        cursor.execute("SELECT id, fullname, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        # user[0] = id, user[1] = fullname, user[2] = password
        if user and check_password_hash(user[2], password):
            
            # --- (تعديل جديد 4) حفظ بيانات المستخدم في الذاكرة ---
            session["user_id"] = user[0]
            session["fullname"] = user[1]
            
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="بيانات الدخول غير صحيحة")

    return render_template("login.html")


# --- (تعديل جديد 5) مسار تسجيل الخروج ---
@app.route("/logout")
def logout():
    session.clear() # يمسح بيانات الجلسة من الذاكرة
    return redirect(url_for("login"))


@app.route("/schedule", methods=["GET", "POST"])
def schedule():
    # حماية الصفحة
    if "user_id" not in session: 
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # إذا قام المستخدم بالضغط على "إضافة" (POST)
    if request.method == "POST":
        day = request.form.get("day")
        subject = request.form.get("subject")
        class_time = request.form.get("class_time") # انتبه غيرنا الاسم ليتطابق مع قاعدة البيانات

        if day and subject and class_time:
            # إدخال الحصة وربطها برقم المستخدم الحالي
            cursor.execute(
                "INSERT INTO schedule (user_id, day, subject, class_time) VALUES (?, ?, ?, ?)",
                (user_id, day, subject, class_time)
            )
            conn.commit()
            return redirect(url_for("schedule"))

    # جلب الحصص الخاصة بهذا المستخدم فقط لكي نعرضها
    cursor.execute("SELECT id, day, subject, class_time FROM schedule WHERE user_id = ?", (user_id,))
    schedule_items = cursor.fetchall()
    conn.close()

    return render_template("schedule.html", schedule_items=schedule_items)


# مسار جديد لحذف الحصة
@app.route("/delete_schedule/<int:item_id>", methods=["POST"])
def delete_schedule(item_id):
    if "user_id" not in session: 
        return redirect(url_for("login"))
        
    user_id = session["user_id"]
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # نحذف الحصة بشرط أن تكون تابعة للمستخدم نفسه (لزيادة الأمان)
    cursor.execute("DELETE FROM schedule WHERE id = ? AND user_id = ?", (item_id, user_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for("schedule"))


@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    # حماية الصفحة
    if "user_id" not in session: 
        return redirect(url_for("login"))
        
    user_id = session["user_id"]
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # استقبال بيانات المهمة الجديدة وحفظها
    if request.method == "POST":
        title = request.form.get("title")
        task_date = request.form.get("task_date")
        task_type = request.form.get("task_type")

        if title and task_date and task_type:
            cursor.execute(
                "INSERT INTO tasks (user_id, title, task_date, task_type) VALUES (?, ?, ?, ?)",
                (user_id, title, task_date, task_type)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("tasks"))

    # جلب مهام هذا المستخدم فقط
    cursor.execute("SELECT id, title, task_date, task_type FROM tasks WHERE user_id = ?", (user_id,))
    task_items = cursor.fetchall()
    conn.close()

    return render_template("tasks.html", task_items=task_items)


# مسار حذف المهمة
@app.route("/delete_task/<int:item_id>", methods=["POST"])
def delete_task(item_id):
    if "user_id" not in session: 
        return redirect(url_for("login"))
        
    user_id = session["user_id"]
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # حذف المهمة الخاصة بهذا المستخدم
    cursor.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (item_id, user_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for("tasks"))


@app.route("/exam", methods=["GET", "POST"])
def exam():
    if "user_id" not in session: return redirect(url_for("login"))
    
    user_id = session["user_id"]
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # استقبال بيانات الامتحان الجديد وحفظها
    if request.method == "POST":
        subject = request.form.get("subject")
        exam_date = request.form.get("exam_date")
        exam_time = request.form.get("exam_time")

        if subject and exam_date and exam_time:
            cursor.execute(
                "INSERT INTO exams (user_id, subject, exam_date, exam_time) VALUES (?, ?, ?, ?)",
                (user_id, subject, exam_date, exam_time)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("exam"))

    # جلب امتحانات المستخدم الحالي فقط
    cursor.execute("SELECT id, subject, exam_date, exam_time FROM exams WHERE user_id = ?", (user_id,))
    exam_items = cursor.fetchall()
    conn.close()

    return render_template("exam.html", exam_items=exam_items)


# مسار حذف الامتحان
@app.route("/delete_exam/<int:item_id>", methods=["POST"])
def delete_exam(item_id):
    if "user_id" not in session: return redirect(url_for("login"))
    
    user_id = session["user_id"]
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # حذف الامتحان الخاص بهذا المستخدم
    cursor.execute("DELETE FROM exams WHERE id = ? AND user_id = ?", (item_id, user_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for("exam"))


@app.route("/bermuda")
def bermuda():
    if "user_id" not in session: return redirect(url_for("login"))
    return render_template("bermuda.html")


if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        Timer(1, lambda: webbrowser.open("http://127.0.0.1:5000/login")).start()
        
    app.run(debug=True)