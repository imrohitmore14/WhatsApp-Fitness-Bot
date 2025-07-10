# 💪 WhatsApp Fitness Bot

This is a Python-based notification bot that sends **daily workout plans via WhatsApp and Email** using **Twilio API** and **SMTP**. It is hosted on **Render** and scheduled using **APScheduler** with logs stored and sent as weekly reports. The system can also be manually triggered via secure API endpoints.

---

## 📦 Features

- 📅 **Automated daily WhatsApp + Email workout reminders** (Morning + Evening)
- 🔐 **Secure manual trigger endpoint** (protected from bots & scrapers)
- 🌐 **Wake-up endpoint** to keep the Render app alive
- 📝 **Workout plans defined in JSON** (`workouts.json`)
- 📧 **Weekly log report** sent via email every Sunday at 9:00 PM
- 🇮🇳 **IST-based logging & scheduling**
- 📜 **Log viewer endpoint** to see all activity in real time

---

## 🛠️ Tech Stack

| Feature                | Technology        |
|------------------------|-------------------|
| Backend Framework      | Flask             |
| Scheduling             | APScheduler       |
| WhatsApp Messaging     | Twilio API        |
| Email Notifications    | SMTP (Gmail)      |
| Hosting                | Render            |
| Logs                   | Python logging    |
| Timezone Support       | pytz              |
| Secure Config          | python-dotenv     |

---

## 📂 Project Structure

```
whatsapp-fitness-bot/
│
├── app.py                    # Main Flask application
├── workouts.json             # Workout schedule (structured JSON)
├── notification_logs.log     # All events are logged here
├── .env                      # Environment config (not committed)
├── requirements.txt          # Python dependencies
```

---

## 🧠 How It Works

### 1. **Workouts Source**
- Exercises for each day are defined inside `workouts.json` in the following format:

```json
{
  "Monday": [
    {
      "exercise": "Bench Press",
      "sets": [
        {"weight": "60kg", "reps": 10},
        {"weight": "65kg", "reps": 8}
      ]
    }
  ]
}
```

### 2. **Scheduled Notifications**

| Message Type | Time       | Platform     |
|--------------|------------|--------------|
| Morning      | 7:00 AM IST | WhatsApp + Email |
| Evening      | 5:00 PM IST | WhatsApp + Email |
| Log Report   | Sunday 9:00 PM IST | Email |

### 3. **Manual Trigger**

Manually trigger the workout notification using a secure tokenized URL:

```
POST https://<your-app>.onrender.com/manual/trigger-workout?token=secure123
```

Protected from:
- Facebook/Twitter/Telegram/WhatsApp/Slack link scrapers
- Unauthorized access via token check

### 4. **Wake-Up Endpoint**

Use this lightweight API to **pre-wake** the Render app before the actual cron hits:

```
GET https://<your-app>.onrender.com/wake-up
```

### 5. **Log Viewer**

Quickly view past activity from the server logs:

```
GET https://<your-app>.onrender.com/logs
```

---

## 🔐 Environment Variables

Create a `.env` file in the root directory:

```env
# Twilio WhatsApp Config
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_auth_token
WHATSAPP_FROM=whatsapp:+14155238886
WHATSAPP_TO=whatsapp:+9198XXXXXXX

# Gmail Email Config
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=your_email@gmail.com

# Manual Trigger Token
MANUAL_TRIGGER_TOKEN=secure123
```

> ⚠️ Use App Password for Gmail (Enable 2FA + Create app-specific password)

---

## 🚀 Deployment on Render

1. Push this project to GitHub
2. Go to [Render.com](https://render.com)
3. Create a new **Web Service**
4. Set the **Start Command** to:

```bash
gunicorn app:app
```

5. Add all `.env` variables under **Environment Settings**
6. Add a **Health Check URL** like `/wake-up`
7. Use [cron-job.org](https://cron-job.org) to hit `/wake-up` **5 mins before each scheduled task**

---

## 📌 Cron Setup (via cron-job.org)

| Purpose         | URL                                             | Time IST        |
|-----------------|--------------------------------------------------|------------------|
| Wake-up Morning | `/wake-up`                                      | 6:55 AM IST      |
| Wake-up Evening | `/wake-up`                                      | 4:55 PM IST      |
| Weekly Report   | `/wake-up`                                      | 8:55 PM IST Sunday |

> ⚠️ Wake-up call ensures Render app is "warm" before the real message-sending job.

---

## 🧪 Testing Locally

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```

---

## ✅ Sample Output

**WhatsApp:**
```
🏋️ Wednesday Workout:
• Squats
   - Set 1: 80kg × 10 reps
   - Set 2: 90kg × 8 reps

🔗 Useful Links:
📬 Send Workout Manually: <url>
📄 View Logs: <url>
```

**Email:**
Subject: 🏋️ Wednesday Workout Plan  
Content: Same as WhatsApp + links.

---

## 📈 Future Enhancements

- User authentication & dashboard
- Admin panel for adding/changing workouts
- Database support (e.g. SQLite or MongoDB)
- Daily reminders via Telegram/Slack too

---

## 🤝 Contributing

Feel free to fork the repo, raise issues, or submit PRs for improvements!

---

## 📄 License

MIT License - Use freely with attribution.