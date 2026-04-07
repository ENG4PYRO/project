import os
from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from db import get_db_connection

schedule_bp = Blueprint('schedule', __name__)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@schedule_bp.route("/schedule", methods=["GET", "POST"])
def schedule_page():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    user_id = session["user_id"]
    
    if request.method == "POST":
        day = request.form.get("day")
        subject = request.form.get("subject")
        class_time = request.form.get("class_time")
        
    
        files = request.files.getlist("material_file")
        saved_paths = []
        

        for file in files:
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                saved_paths.append(f"uploads/{filename}")

        
        file_path_string = "|".join(saved_paths)

        conn = get_db_connection()
        conn.execute("INSERT INTO schedule (user_id, day, subject, class_time, file_path) VALUES (?, ?, ?, ?, ?)", 
                     (user_id, day, subject, class_time, file_path_string))
        conn.commit()
        conn.close()
        return redirect(url_for("schedule.schedule_page"))
        
    conn = get_db_connection()
    schedule_items = conn.execute("SELECT id, day, subject, class_time, file_path FROM schedule WHERE user_id = ?", (user_id,)).fetchall()
    user_data = conn.execute("SELECT main_schedule_path FROM users WHERE id = ?", (user_id,)).fetchone()
    main_schedule_path = user_data[0] if user_data and user_data[0] else ""
    conn.close()
    
    return render_template("schedule.html", schedule_items=schedule_items, main_schedule_path=main_schedule_path)

@schedule_bp.route("/upload_main_schedule", methods=["POST"])
def upload_main_schedule():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    user_id = session["user_id"]
    
    file = request.files.get("main_schedule_file")
    if file and file.filename != '':
        filename = f"user_{user_id}_schedule_{secure_filename(file.filename)}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        
        conn = get_db_connection()
        conn.execute("UPDATE users SET main_schedule_path = ? WHERE id = ?", (f"uploads/{filename}", user_id))
        conn.commit()
        conn.close()
        
    return redirect(url_for("schedule.schedule_page"))

@schedule_bp.route("/delete_schedule/<int:item_id>", methods=["POST"])
def delete_schedule(item_id):
    if "user_id" not in session: return redirect(url_for("auth.login"))
    conn = get_db_connection()
    conn.execute("DELETE FROM schedule WHERE id = ? AND user_id = ?", (item_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("schedule.schedule_page"))