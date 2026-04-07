import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")

def send_notification(user_email, user_name, item_title, item_date, item_time, item_type):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = user_email
    msg['Subject'] = f"تنبيه: {item_title} يقترب موعده!"


    html = f"""
    <div dir="rtl" style="font-family: Arial, sans-serif; border: 1px solid #4353ff; padding: 20px; border-radius: 10px;">
        <h2 style="color: #4353ff;">مرحباً {user_name} 👋</h2>
        <p>نود تذكيرك بأن لديك <strong>{item_type}</strong> قادم:</p>
        <div style="background: #f5f7ff; padding: 15px; border-radius: 8px; border-right: 5px solid #4353ff;">
            <p>📌 <strong>العنوان:</strong> {item_title}</p>
            <p>📅 <strong>التاريخ:</strong> {item_date}</p>
            <p>⏰ <strong>الوقت:</strong> {item_time}</p>
        </div>
        <p style="margin-top: 20px; color: #666;">نتمنى لك التوفيق في دراستك! 🎓</p>
    </div>
    """
    
    msg.attach(MIMEText(html, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, user_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    
def send_weekly_report(user_email, user_name, completed_tasks, total_hours, upcoming_exams):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = user_email
    msg['Subject'] = "📊 تقريرك الأسبوعي من المساعد الدراسي!"


    html = f"""
    <div dir="rtl" style="font-family: Arial, sans-serif; border: 1px solid #34c759; padding: 20px; border-radius: 10px; max-width: 600px; margin: auto;">
        <h2 style="color: #34c759; text-align: center;">مرحباً {user_name} 👋، نهاية أسبوع سعيدة!</h2>
        <p style="font-size: 16px; color: #333; text-align: center;">إليك ملخص إنجازاتك هذا الأسبوع. نحن فخورون بك!</p>
        
        <div style="background: #eefbee; padding: 20px; border-radius: 8px; border-right: 5px solid #34c759; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #28a745;">📈 إحصائياتك:</h3>
            <p style="font-size: 16px;">✅ <strong>المهام التي أنجزتها:</strong> <span style="color:#4353ff; font-weight:bold;">{completed_tasks} مهام</span></p>
            <p style="font-size: 16px;">⏱️ <strong>ساعات دراستك:</strong> <span style="color:#ff9500; font-weight:bold;">{total_hours} ساعة</span></p>
            <p style="font-size: 16px;">📘 <strong>الامتحانات القادمة:</strong> <span style="color:#d32f2f; font-weight:bold;">{upcoming_exams} امتحانات</span></p>
        </div>
        
        <p style="color: #666; text-align: center; font-size: 14px;">استرح جيداً في هذه العطلة، واستعد لأسبوع جديد مليء بالنجاح والتفوق! 🚀</p>
    </div>
    """
    
    msg.attach(MIMEText(html, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, user_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"⚠️ فشل إرسال التقرير الأسبوعي. التفاصيل: {e}")
        return False