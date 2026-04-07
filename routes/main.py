from flask import Blueprint, render_template, redirect, url_for, session
from db import get_db_connection
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    return render_template("home.html")

@main_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    user_id = session["user_id"]
    conn = get_db_connection()
    user = conn.execute("SELECT fullname FROM users WHERE id = ?", (user_id,)).fetchone()
    
    total_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (user_id,)).fetchone()[0]
    completed_count = conn.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'منجزة'", (user_id,)).fetchone()[0]
    total_exams = conn.execute("SELECT COUNT(*) FROM exams WHERE user_id = ?", (user_id,)).fetchone()[0]
    
    tasks_data = conn.execute("SELECT duration FROM tasks WHERE user_id = ? AND status = 'منجزة'", (user_id,)).fetchall()
    total_hours = 0
    for task in tasks_data:
        try: total_hours += float(task[0])
        except: pass
        
    conn.close()
    return render_template("dashboard.html", fullname=user[0], total_tasks=total_tasks, completed_count=completed_count, total_exams=total_exams, total_hours=total_hours)


@main_bp.route("/download_report")
def download_report():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    user_id = session["user_id"]
    
    conn = get_db_connection()
    user = conn.execute("SELECT fullname, email FROM users WHERE id = ?", (user_id,)).fetchone()
    today_date = datetime.now().strftime('%Y-%m-%d')
    

    completed_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'منجزة'", (user_id,)).fetchone()[0]
    
    tasks_data = conn.execute("SELECT duration FROM tasks WHERE user_id = ? AND status = 'منجزة'", (user_id,)).fetchall()
    total_hours = sum([float(t[0]) for t in tasks_data if t[0]])
        
    upcoming_exams = conn.execute("SELECT COUNT(*) FROM exams WHERE user_id = ? AND exam_date >= ?", (user_id, today_date)).fetchone()[0]
    conn.close()
    
    return render_template("report.html", 
                           fullname=user[0], email=user[1], 
                           completed_tasks=completed_tasks, 
                           total_hours=total_hours, 
                           upcoming_exams=upcoming_exams, today_date=today_date)

@main_bp.route("/bermuda")
def bermuda():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    return render_template("bermuda.html")