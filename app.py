from flask import Flask, jsonify
from datetime import datetime
import json
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import ConflictingIdError
import pytz
import logging

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set up logging
class ISTFormatter(logging.Formatter):
    def converter(self, timestamp):
        ist = pytz.timezone("Asia/Kolkata")
        dt = datetime.fromtimestamp(timestamp, tz=ist)
        return dt

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat()

# Set up logging with IST formatter
LOG_FILE = 'notification_logs.log'
formatter = ISTFormatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO, handlers=[file_handler])

# Load workout data
with open('workouts.json', 'r') as f:
    workouts = json.load(f)

# Twilio credentials (set these as environment variables or paste here carefully)
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
WHATSAPP_FROM = os.getenv('WHATSAPP_FROM')
WHATSAPP_TO = os.getenv('WHATSAPP_TO')

# Email setup
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_TO = os.getenv('EMAIL_TO')

def format_workout_message(day):
    day_workout = workouts.get(day, [])
    if not day_workout:
        return f"🏋️ {day} Workout: Rest Day 🏊"

    message_lines = [f"🏋️ {day} Workout:"]
    for ex in day_workout:
        message_lines.append(f"• {ex['exercise']}")
        for idx, s in enumerate(ex['sets'], 1):
            message_lines.append(f"   - Set {idx}: {s['weight']} × {s['reps']} reps")
    return "\n".join(message_lines)

#Function to send email with today's workout
def send_email_message():
    today = datetime.today().strftime('%A')
    body = format_workout_message(today)

    # Add useful links to the email message
    body += (
        "\n\n🔗 Useful Links:\n"
        "📬 Send Workout Manually: https://whatsapp-fitness-bot.onrender.com/send-today-workout\n"
        "📄 View Logs: https://whatsapp-fitness-bot.onrender.com/logs"
    )

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_TO
    msg['Subject'] = f"🏋️ {today} Workout Plan"
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, EMAIL_TO, msg.as_string())
        server.quit()
        print(f"📧 Email sent to {EMAIL_TO}")
        logging.info(f"Email sent successfully for {today} to {EMAIL_TO}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        logging.error(f"Failed to send email for {today}: {e}")

# Function to send WhatsApp message with today's workout
def send_whatsapp_message():
    today = datetime.today().strftime('%A')
    body = format_workout_message(today)

    # Add useful links to the WhatsApp message
    body += (
        "\n\n🔗 *Useful Links:*\n"
        "📬 Send Workout Manually: https://whatsapp-fitness-bot.onrender.com/send-today-workout\n"
        "📄 View Logs: https://whatsapp-fitness-bot.onrender.com/logs"
    )

    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    try:
        message = client.messages.create(
            body=body,
            from_=WHATSAPP_FROM,
            to=WHATSAPP_TO
        )
        print(f"✅ WhatsApp sent for {today}: SID={message.sid}")
        logging.info(f"WhatsApp sent successfully for {today}: SID={message.sid}")
    except Exception as e:
        print(f"❌ Failed to send WhatsApp: {e}")
        logging.error(f"Failed to send WhatsApp for {today}: {e}\nMessage body:\n{body}")

# Function to send weekly log report via email
def send_log_report():
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_TO
    msg['Subject'] = "📅 Weekly Notification Log Report"

    try:
        with open(LOG_FILE, 'r') as f:
            log_content = f.read()
        msg.attach(MIMEText(log_content, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, EMAIL_TO, msg.as_string())
        server.quit()

        print("📧 Log report sent via email")
        logging.info("Weekly log report sent via email")
    except Exception as e:
        print(f"❌ Failed to send log report: {e}")
        logging.error(f"Failed to send weekly log report: {e}")

# Flask route to get today's workout
@app.route('/send-today-workout', methods=['GET'])
def trigger_workout():
    send_whatsapp_message()
    send_email_message()
    return jsonify({"status": "Messages sent successfully."})


@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with open(LOG_FILE, 'r') as f:
            return f.read(), 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        return str(e), 500

# Schedule reminders
scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Kolkata'))

try:
    scheduler.add_job(send_whatsapp_message, 'cron', hour=7, minute=0, id='whatsapp_morning')
    scheduler.add_job(send_whatsapp_message, 'cron', hour=17, minute=0, id='whatsapp_evening')
    scheduler.add_job(send_email_message, 'cron', hour=7, minute=0, id='email_morning')
    scheduler.add_job(send_email_message, 'cron', hour=17, minute=0, id='email_evening')
    scheduler.add_job(send_log_report, 'cron', day_of_week='sun', hour=21, minute=0, id='weekly_log')
except ConflictingIdError:
    pass  

# Prevent duplicate jobs if already added

# Start scheduler only if not already running
if __name__ != '__main__' and not scheduler.running:
    scheduler.start()
    logging.info("Scheduler started (production)")

if __name__ == '__main__':
    if not scheduler.running:
        scheduler.start()
        logging.info("Scheduler started (local)")
    app.run(debug=True)
