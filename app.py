import os
import webbrowser
from threading import Timer
from datetime import datetime
from flask import Flask
from flask_apscheduler import APScheduler
from db import init_db, get_db_connection
from mailer import send_notification, send_weekly_report
from dotenv import load_dotenv
from routes.auth import auth_bp
from routes.main import main_bp
from routes.tasks import tasks_bp
from routes.schedule import schedule_bp
from routes.exams import exams_bp



load_dotenv() 

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback_super_secret_key")


init_db()


scheduler = APScheduler()

def check_notifications():
    with app.app_context():
        conn = get_db_connection()
        now = datetime.now()
        today_date = now.strftime('%Y-%m-%d')
        print(f"--- فحص الإشعارات الآن: {now.strftime('%H:%M')} ---") # رسالة تشخيصية
        
        tasks = conn.execute("""
            SELECT tasks.id, users.email, users.fullname, tasks.title, tasks.task_date, tasks.task_time, tasks.task_type, tasks.reminder_hours 
            FROM tasks JOIN users ON tasks.user_id = users.id 
            WHERE tasks.task_date = ? AND tasks.notification_sent = 0
        """, (today_date,)).fetchall()

        for task in tasks:
            task_time_str = task[5]
            reminder_h = float(task[7]) if task[7] else 2.0
            
            if task_time_str:
                try:
        
                    t_time = task_time_str.strip()
                    exact_task_time = datetime.strptime(f"{task[4]} {t_time}", '%Y-%m-%d %H:%M')
                    time_diff = exact_task_time - now
                    hours_diff = time_diff.total_seconds() / 3600
                    
                    print(f"المهمة: {task[3]} | الوقت المتبقي: {hours_diff:.2f} ساعة | ساعات التذكير المطلوبة: {reminder_h}")


                    if 0 < hours_diff <= reminder_h:
                        if send_notification(task[1], task[2], task[3], task[4], task_time_str, task[6]):
                            conn.execute("UPDATE tasks SET notification_sent = 1 WHERE id = ?", (task[0],))
                            print(f"✅ تم إرسال إشعار: {task[3]}")
                except Exception as e:
                    print(f"❌ خطأ في تحليل وقت المهمة {task[3]}: {e}")
            else:
              
                if send_notification(task[1], task[2], task[3], task[4], "غير محدد", task[6]):
                    conn.execute("UPDATE tasks SET notification_sent = 1 WHERE id = ?", (task[0],))
        
        conn.commit()
        conn.close()


scheduler.add_job(id='notify_job', func=check_notifications, trigger='interval', minutes=1)
scheduler.start()

def generate_weekly_reports():
    with app.app_context():
        conn = get_db_connection()
        users = conn.execute("SELECT id, email, fullname FROM users").fetchall()
        today_date = datetime.now().strftime('%Y-%m-%d')
        
        for user in users:
            user_id = user[0]
            user_email = user[1]
            user_name = user[2]
     
            completed_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'منجزة'", (user_id,)).fetchone()[0]
            
            
            tasks_data = conn.execute("SELECT duration FROM tasks WHERE user_id = ? AND status = 'منجزة'", (user_id,)).fetchall()
            total_hours = 0
            for task in tasks_data:
                try:
                    total_hours += float(task[0])
                except: pass
            
          
            upcoming_exams = conn.execute("SELECT COUNT(*) FROM exams WHERE user_id = ? AND exam_date >= ?", (user_id, today_date)).fetchone()[0]
            
      
            send_weekly_report(user_email, user_name, completed_tasks, total_hours, upcoming_exams)
            
        conn.close()


scheduler.add_job(id='weekly_report_job', func=generate_weekly_reports, trigger='cron', day_of_week='fri', hour=20, minute=0)



app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(schedule_bp)
app.register_blueprint(exams_bp)


if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":

        Timer(1, lambda: webbrowser.open("http://127.0.0.1:5000/login")).start()
    app.run(debug=True)