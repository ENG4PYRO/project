from flask import Blueprint, render_template, session, redirect, url_for
from db import get_db_connection

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    return render_template("home.html")

@main_bp.route("/bermuda")
def bermuda():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    return render_template("bermuda.html")

@main_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    user_id = session["user_id"]
    conn = get_db_connection()
    
    total_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE user_id=?", (user_id,)).fetchone()[0]
    completed_tasks = conn.execute("SELECT duration FROM tasks WHERE user_id=? AND status='منجزة'", (user_id,)).fetchall()
    total_exams = conn.execute("SELECT COUNT(*) FROM exams WHERE user_id=?", (user_id,)).fetchone()[0]
    conn.close()

    completed_count = len(completed_tasks)
    total_hours = 0
    for task in completed_tasks:
        try:
            total_hours += float(task[0])
        except (ValueError, TypeError):
            pass

    return render_template("dashboard.html", fullname=session.get("fullname"), total_tasks=total_tasks, completed_count=completed_count, total_hours=total_hours, total_exams=total_exams)