from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password")
        if password != request.form.get("confirmpassword"): return render_template("signup.html", error="كلمات المرور غير متطابقة")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)", (fullname, email, generate_password_hash(password)))
            conn.commit()
            conn.close()

            return redirect(url_for("auth.login")) 
        except: return render_template("signup.html", error="الإيميل مستخدم مسبقاً")
    return render_template("signup.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, fullname, password FROM users WHERE email = ?", (request.form.get("email"),))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[2], request.form.get("password")):
            session["user_id"] = user[0]
            session["fullname"] = user[1]
            return redirect(url_for("main.home"))
        return render_template("login.html", error="بيانات الدخول غير صحيحة")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))