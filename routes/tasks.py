from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_db_connection

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route("/tasks", methods=["GET", "POST"])
def tasks_page():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    user_id = session["user_id"]
    conn = get_db_connection()
    if request.method == "POST":
        reminder_hours = request.form.get("reminder_hours", 2)
        conn.execute("INSERT INTO tasks (user_id, title, task_date, task_time, duration, task_type, reminder_hours) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, request.form.get("title"), request.form.get("task_date"), request.form.get("task_time"), request.form.get("duration"), request.form.get("task_type"), reminder_hours))
        conn.commit()
        conn.close()
        return redirect(url_for("tasks.tasks_page"))
    
    task_items = conn.execute("SELECT id, title, task_date, task_time, duration, task_type, status, reminder_hours FROM tasks WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return render_template("tasks.html", task_items=task_items)

@tasks_bp.route("/complete_task/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    if "user_id" not in session: return redirect(url_for("auth.login"))
    conn = get_db_connection()
    conn.execute("UPDATE tasks SET status='منجزة' WHERE id=? AND user_id=?", (task_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("tasks.tasks_page"))

@tasks_bp.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    if "user_id" not in session: return redirect(url_for("auth.login"))
    user_id = session["user_id"]
    conn = get_db_connection()
    if request.method == "POST":
        reminder_hours = request.form.get("reminder_hours", 2)
        conn.execute("UPDATE tasks SET title=?, task_date=?, task_time=?, duration=?, task_type=?, reminder_hours=? WHERE id=? AND user_id=?", 
                     (request.form.get("title"), request.form.get("task_date"), request.form.get("task_time"), request.form.get("duration"), request.form.get("task_type"), reminder_hours, task_id, user_id))
        conn.commit()
        conn.close()
        return redirect(url_for("tasks.tasks_page"))

    task = conn.execute("SELECT id, title, task_date, task_time, duration, task_type, reminder_hours FROM tasks WHERE id=? AND user_id=?", (task_id, user_id)).fetchone()
    conn.close()
    return render_template("edit_task.html", task=task)

@tasks_bp.route("/delete_task/<int:item_id>", methods=["POST"])
def delete_task(item_id):
    if "user_id" not in session: return redirect(url_for("auth.login"))
    conn = get_db_connection()
    conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (item_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("tasks.tasks_page"))