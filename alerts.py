import os
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# --------------------------------
# Email Configuration
# --------------------------------
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

SENDER_EMAIL = os.getenv("SENDER_EMAIL", "devil8887777@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "vjstskpkitvzuusc")   # replace with NEW app password

RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "devil8887777@gmail.com")

EMAIL_ALERTS_ENABLED = os.getenv("ENABLE_EMAIL_ALERTS", "false").lower() in ("1", "true", "yes")


# --------------------------------
# Send Email Alert
# --------------------------------
def send_email_alert(subject, message):

    server = None

    try:
        print("[INFO] Connecting to Gmail SMTP...")

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)

        server.ehlo()
        server.starttls()
        server.ehlo()

        print("[INFO] Logging in...")

        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        print("[INFO] Login successful. Sending email...")

        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "plain"))

        server.send_message(msg)

        print("[ALERT] Email notification sent successfully")

    except Exception as e:
        print("[ALERT ERROR]", e)

    finally:
        if server:
            server.quit()


# --------------------------------
# Trigger Alert for Attacks
# --------------------------------
def process_alerts(alerts):

    import datetime

    print("[DEBUG] Alerts detected:", alerts)

    if not alerts:
        print("[DEBUG] No alerts to process")
        return

    if not EMAIL_ALERTS_ENABLED:
        print("[DEBUG] Email alerts disabled. Skipping email delivery.")
        return

    sent_ips = set()

    for alert in alerts:

        severity = alert.get("severity")
        ip = alert.get("ip")

        print(f"[DEBUG] Processing alert with severity: {severity}")

        if severity in ["CRITICAL"]:

            if ip in sent_ips:
                continue

            subject = f"🚨 CRITICAL ALERT: {alert.get('type')} from {ip}"

            current_time = datetime.datetime.now()

            message = f"""
🚨 LogSentrix Security Alert

Time        : {current_time}
Attack Type : {alert.get("type")}
IP Address  : {ip}
Attempts    : {alert.get("attempts")}
Severity    : {severity}

Immediate investigation recommended.
"""

            thread = threading.Thread(target=send_email_alert, args=(subject, message), daemon=True)
            thread.start()

            sent_ips.add(ip)