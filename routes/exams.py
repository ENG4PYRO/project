from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_db_connection

exams_bp = Blueprint('exams', __name__)

@exams_bp.route("/exam", methods=["GET", "POST"])
def exam_page():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    user_id = session["user_id"]
    conn = get_db_connection()
    if request.method == "POST":
        conn.execute("INSERT INTO exams (user_id, subject, exam_date, exam_time) VALUES (?, ?, ?, ?)", (user_id, request.form.get("subject"), request.form.get("exam_date"), request.form.get("exam_time")))
        conn.commit()
        conn.close()
        return redirect(url_for("exams.exam_page"))
    exam_items = conn.execute("SELECT id, subject, exam_date, exam_time FROM exams WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return render_template("exam.html", exam_items=exam_items)

@exams_bp.route("/delete_exam/<int:item_id>", methods=["POST"])
def delete_exam(item_id):
    if "user_id" not in session: return redirect(url_for("auth.login"))
    conn = get_db_connection()
    conn.execute("DELETE FROM exams WHERE id = ? AND user_id = ?", (item_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("exams.exam_page"))