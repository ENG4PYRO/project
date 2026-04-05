from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_db_connection

schedule_bp = Blueprint('schedule', __name__)

@schedule_bp.route("/schedule", methods=["GET", "POST"])
def schedule_page():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    user_id = session["user_id"]
    if request.method == "POST":
        conn = get_db_connection()
        conn.execute("INSERT INTO schedule (user_id, day, subject, class_time) VALUES (?, ?, ?, ?)", (user_id, request.form.get("day"), request.form.get("subject"), request.form.get("class_time")))
        conn.commit()
        conn.close()
        return redirect(url_for("schedule.schedule_page"))
    conn = get_db_connection()
    schedule_items = conn.execute("SELECT id, day, subject, class_time FROM schedule WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return render_template("schedule.html", schedule_items=schedule_items)

@schedule_bp.route("/delete_schedule/<int:item_id>", methods=["POST"])
def delete_schedule(item_id):
    if "user_id" not in session: return redirect(url_for("auth.login"))
    conn = get_db_connection()
    conn.execute("DELETE FROM schedule WHERE id = ? AND user_id = ?", (item_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("schedule.schedule_page"))