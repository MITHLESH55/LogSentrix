# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("[WARNING] python-dotenv not installed. Environment variables must be set manually.")

from ip_lookup import check_ip_reputation, get_ip_info

from collections import Counter
from pathlib import Path
import numpy as np
from sklearn.ensemble import IsolationForest
import logging
import sys
import sqlite3

from flask import Flask, render_template, jsonify, redirect, url_for, request, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from parser import parse_logs
from detector import detect_threat
from ai_detector import detect_anomaly
from database import init_db, insert_logs, get_user, create_user, update_last_login
from alerts import process_alerts

import pandas as pd
# Suppress pandas SettingWithCopyWarning
pd.options.mode.chained_assignment = None
import time
import threading

# ================================================================
# LOGGING CONFIGURATION FOR DEBUGGING
# ================================================================
def setup_logging():
    """Configure logging for better error tracking."""
    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "app.log"
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(str(log_file)),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

logger = setup_logging()

# ================================================================
# FLASK APP INITIALIZATION
# ================================================================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production-12345'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# ================================================================
# DATABASE INITIALIZATION ON APP START
# ================================================================
def init_app_database():
    """Initialize database when Flask app starts."""
    try:
        logger.info("=" * 80)
        logger.info("🚀 LogSentrix Starting Up")
        logger.info("=" * 80)
        init_db()
        logger.info("✅ Database initialization completed successfully")
        return True
    except Exception as e:
        logger.critical(f"❌ CRITICAL: Database initialization failed: {e}", exc_info=True)
        print(f"[CRITICAL] Database initialization failed: {e}")
        return False

# Initialize database on app startup
with app.app_context():
    if not init_app_database():
        logger.error("Continuing with uninitialized database. Registration will fail.")
        print("[ERROR] Database failed to initialize. Some features may not work.")

# ================================================================
# FLASK-LOGIN SETUP
# ================================================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access the security dashboard.'
login_manager.login_message_category = 'info'

# ================================================================
# USER MODEL
# ================================================================
class User(UserMixin):
    """User model for Flask-Login."""
    
    def __init__(self, username, password_hash=None):
        self.id = username
        self.username = username
        self.password_hash = password_hash
    
    def check_password(self, password):
        """Verify password against hash."""
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def __repr__(self):
        return f'<User {self.username}>'


# ================================================================
# LOGIN MANAGER CALLBACK
# ================================================================
@login_manager.user_loader
def load_user(user_id):
    """Load user from database."""
    user_data = get_user(user_id)
    if user_data:
        return User(user_data['username'], user_data['password_hash'])
    return None


# ================================================================
# AUTHENTICATION ROUTES
# ================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember_me')
        
        # Validate input
        if not username or not password:
            logger.warning(f"Login attempt with missing credentials from {request.remote_addr}")
            return render_template('login.html', error='Username and password are required.'), 401
        
        # Find user from database
        user_data = get_user(username)
        
        # Verify credentials
        if user_data is None or not check_password_hash(user_data['password_hash'], password):
            logger.warning(f"Failed login attempt for user '{username}' from {request.remote_addr}")
            return render_template('login.html', error='Invalid username or password.'), 401
        
        # Create user object for Flask-Login
        user = User(user_data['username'], user_data['password_hash'])
        
        # Log the user in
        login_user(user, remember=remember)
        update_last_login(username)
        logger.info(f"User '{username}' logged in successfully from {request.remote_addr}")
        
        # Redirect to dashboard or next page
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration with detailed error logging."""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validate input
        if not username or not password or not confirm_password:
            logger.warning(f"Registration attempt with missing fields from {request.remote_addr}")
            return render_template('register.html', error='All fields are required.'), 400
        
        # Check username length
        if len(username) < 3:
            logger.warning(f"Registration with short username '{username}' from {request.remote_addr}")
            return render_template('register.html', error='Username must be at least 3 characters long.'), 400
        
        # Check password length
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters long.'), 400
        
        # Check if passwords match
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match.'), 400
        
        # Check if username already exists in database
        try:
            if get_user(username):
                logger.warning(f"Registration attempt with existing username: {username} from {request.remote_addr}")
                return render_template('register.html', error='Username already exists. Please choose another.'), 400
        except Exception as e:
            logger.error(f"Error checking existing user '{username}': {e}", exc_info=True)
            return render_template('register.html', error='Database error while checking username. Please try again.'), 500
        
        # Create new user in database
        try:
            logger.info(f"Attempting to register new user: {username} from {request.remote_addr}")
            hashed_pw = generate_password_hash(password)
            
            # Call create_user with full error context
            result = create_user(username, hashed_pw)
            
            if result:
                logger.info(f"✅ User registration successful: {username}")
                return render_template('register.html', success='Account created successfully! You can now login.'), 200
            else:
                logger.warning(f"User creation returned False for: {username}")
                return render_template('register.html', error='Username already exists or registration failed. Please try again.'), 400
                
        except sqlite3.IntegrityError as e:
            logger.error(f"Database integrity error during registration of '{username}': {e}", exc_info=True)
            return render_template('register.html', error='Username already exists or database error. Please try again.'), 400
        except RuntimeError as e:
            logger.error(f"Runtime error during user creation: {e}", exc_info=True)
            return render_template('register.html', error=f'Database error: {str(e)}'), 500
        except Exception as e:
            logger.error(f"Unexpected error registering user {username}: {type(e).__name__}: {e}", exc_info=True)
            return render_template('register.html', error='An unexpected error occurred during registration. Please try again.'), 500
    
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    username = current_user.username
    logout_user()
    logger.info(f"User '{username}' logged out successfully")
    return redirect(url_for('login'))

LOG_FILE = str(Path(__file__).resolve().parent / "logs" / "server.log")

# track log count for monitoring
LAST_LOG_COUNT = 0


def check_new_logs(df):
    global LAST_LOG_COUNT

    current_count = len(df)

    if current_count > LAST_LOG_COUNT:
        print(f"[INFO] New logs detected: {current_count}")

    LAST_LOG_COUNT = current_count


def get_threat_source(alert):
    """
    Determine threat source/classification for an alert.
    
    Combines multiple signals:
    1. IP-based reputation (via check_ip_reputation)
    2. Attack severity/attempt volume
    3. Attack type indicators
    
    Returns the most severe classification.
    """
    ip = alert.get("ip", "")
    severity = alert.get("severity", "").upper()
    attempts = int(alert.get("attempts", 0) or 0)
    alert_type = alert.get("type", "").lower()

    # Handle "Multiple" IPs (distributed attacks)
    if ip == "Multiple":
        if attempts >= 10:
            return "Suspicious Login Storm"
        return "Suspicious"

    # Get IP reputation from threat intelligence system
    try:
        ip_reputation = check_ip_reputation(ip)
    except Exception as e:
        print(f"[ERROR] Failed to get IP reputation for {ip}: {e}")
        ip_reputation = "Low Risk"  # Safe default

    # Escalate based on attack severity and attempt volume
    if severity == "CRITICAL" or attempts > 100:
        return "Confirmed Malicious"
    
    if severity == "HIGH" or attempts > 50:
        return "Likely Malicious"
    
    if severity == "MEDIUM" or attempts > 20:
        return "Suspicious"

    # Use API reputation if available and higher than base assessment
    if ip_reputation == "Malicious":
        return "Malicious"
    elif ip_reputation == "Suspicious":
        return "Suspicious"

    if alert_type == "password spray":
        return "Password Spray"
    if alert_type == "brute force attack":
        return "Brute Force"

    # Default to reputation assessment
    return ip_reputation


# -------------------------------
# Real-time log monitoring thread
# -------------------------------
def monitor_logs():

    global LAST_LOG_COUNT

    while True:

        try:

            df = parse_logs(LOG_FILE)

            if df is not None:

                current_count = len(df)

                if current_count > LAST_LOG_COUNT:
                    print(f"[REALTIME] New logs detected: {current_count}")

                LAST_LOG_COUNT = current_count

        except Exception as e:
            print("[MONITOR ERROR]", e)

        time.sleep(5)


@app.route("/")
@login_required
def dashboard():

    try:
        # parse logs
        df = parse_logs(LOG_FILE)

        if df is None or len(df) == 0:
            df = pd.DataFrame(columns=["time", "status", "user", "ip"])
            
        # insert logs
        insert_logs(df)

        # threat detection
        alerts = detect_threat(df)

        # Enrich alerts with location data
        for alert in alerts:
            ip = alert.get("ip")
            info = get_ip_info(ip)
            alert["country"] = info.get("country", "Unknown")
            alert["city"] = info.get("city", "-")
            alert["lat"] = info.get("lat", 0.0)
            alert["lon"] = info.get("lon", 0.0)
            alert["threat_source"] = get_threat_source(alert)
            
            # Determine source type
            if alert["ip"] == "Multiple":
                alert["source_type"] = "Multiple"
            elif alert["ip"].startswith(("192.168.", "127.", "10.")):
                alert["source_type"] = "Local"
            else:
                alert["source_type"] = "External"

        process_alerts(alerts)

        # top risky locations
        from collections import Counter
        # top risky locations
        risky_locations = Counter(alert.get("country", "Unknown") for alert in alerts if alert.get("country") != "Local")
        top_risky = dict(risky_locations.most_common(5))

        # existing AI anomaly module
        anomalies_list = detect_anomaly(df)

        # metrics
        total_logs = int(len(df))
        failed_logs = int(len(df[df["status"] == "FAILED"]))

        # attack analysis by IP
        failed_df = df[df["status"] == "FAILED"]
        if not failed_df.empty:
            failed_by_ip = failed_df["ip"].value_counts().head(10)
            ip_labels = list(failed_by_ip.index)
            ip_values = [int(v) for v in failed_by_ip.values]
            top_ip = ip_labels[0]
            top_attackers = {ip: int(count) for ip, count in failed_by_ip.head(5).items()}
        else:
            ip_labels = []
            ip_values = []
            top_ip = "None"
            top_attackers = {}

        # -------------------------------
        # Isolation Forest AI Detection
        # -------------------------------
        anomalies_ml = 0
        try:
            failed_attempt_counts = list(top_attackers.values())
            if len(failed_attempt_counts) > 1:
                data = np.array(failed_attempt_counts).reshape(-1, 1)
                model = IsolationForest(contamination=0.2, random_state=42)
                model.fit(data)
                predictions = model.predict(data)
                anomalies_ml = int(sum(predictions == -1))
        except Exception as e:
            logger.error(f"AI Detection error: {e}")
            anomalies_ml = 0

        # attack trend by failed attempts over time
        trend_labels = []
        trend_values = []
        if not failed_df.empty:
            try:
                # Ensure 'time' is datetime
                if not pd.api.types.is_datetime64_any_dtype(failed_df["time"]):
                    failed_df["time"] = pd.to_datetime(failed_df["time"], errors='coerce')
                
                trend = failed_df.groupby(failed_df["time"].dt.strftime("%H:%M")).size()
                trend_labels = list(trend.index)
                trend_values = [int(v) for v in trend.values]
            except Exception as e:
                print(f"[ERROR] Trend calculation: {e}")

        return render_template(
            "dashboard.html",
            total=total_logs,
            failed=failed_logs,
            alerts=alerts,
            anomalies=anomalies_ml,
            ip_labels=ip_labels,
            ip_values=ip_values,
            trend_labels=trend_labels,
            trend_values=trend_values,
            top_ip=top_ip,
            top_attackers=top_attackers,
            top_risky=top_risky,
            current_user=current_user
        )

    except Exception as e:
        import traceback
        error_msg = f"[ERROR] Dashboard: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        with open("app_debug.log", "a") as f:
            f.write(f"--- DASHBOARD ERROR ---\n")
            f.write(error_msg + "\n")
        
        return render_template(
            "dashboard.html",
            total=0,
            failed=0,
            alerts=[],
            anomalies=0,
            ip_labels=[],
            ip_values=[],
            trend_labels=[],
            trend_values=[],
            top_ip="None",
            top_attackers={},
            top_risky={}
        )


@app.route("/data")
@login_required
def get_data():
    """
    API endpoint for real-time dashboard updates.
    Returns JSON data for all dashboard metrics and alerts.
    """
    try:
        print(f"[DEBUG] API requesting data. Reading: {LOG_FILE}")
        df = parse_logs(LOG_FILE)
        print(f"[DEBUG] API Parsed logs: {len(df) if df is not None else 'None'} records")
        if df is None or len(df) == 0:
            df = pd.DataFrame(columns=["time", "status", "user", "ip"])

        alerts = detect_threat(df)
        for alert in alerts:
            ip = alert.get("ip")
            info = get_ip_info(ip)
            alert["country"] = info["country"]
            alert["city"] = info["city"]
            alert["lat"] = info["lat"]
            alert["lon"] = info["lon"]
            alert["threat_source"] = get_threat_source(alert)
            
            # Determine source type (Local/External/Multiple)
            if alert["ip"] == "Multiple":
                alert["source_type"] = "Multiple"
            elif alert["ip"].startswith(("192.168.", "127.", "10.")):
                alert["source_type"] = "Local"
            else:
                alert["source_type"] = "External"

        process_alerts(alerts)

        total_logs = int(len(df))
        failed_df = df[df["status"] == "FAILED"]
        failed_logs = int(len(failed_df))

        if not failed_df.empty:
            failed_by_ip = failed_df["ip"].value_counts().head(10)
            ip_labels = list(failed_by_ip.index)
            ip_values = [int(v) for v in failed_by_ip.values]
        else:
            ip_labels = []
            ip_values = []

        trend_labels = []
        trend_values = []
        if not failed_df.empty:
            try:
                if not pd.api.types.is_datetime64_any_dtype(failed_df["time"]):
                    failed_df["time"] = pd.to_datetime(failed_df["time"], errors='coerce')
                trend = failed_df.groupby(failed_df["time"].dt.strftime("%H:%M")).size()
                trend_labels = list(trend.index)
                trend_values = [int(v) for v in trend.values]
            except Exception as e:
                print(f"[ERROR] API Trend calculation: {e}")

        risky_locations = Counter(alert["country"] for alert in alerts if alert.get("country") and alert["country"] != "Local")
        top_risky = dict(risky_locations.most_common(5))

        return jsonify({
            "total": total_logs,
            "failed": failed_logs,
            "alerts": alerts,
            "ip_labels": ip_labels,
            "ip_values": ip_values,
            "trend_labels": trend_labels,
            "trend_values": trend_values,
            "top_risky": top_risky
        })
    except Exception as e:
        return jsonify({"error": str(e)})


import os

if __name__ == "__main__":
    # initialize database tables at startup
    init_db()

    # start real-time log monitoring
    monitor_thread = threading.Thread(target=monitor_logs)
    monitor_thread.daemon = True
    monitor_thread.start()

    # get port from environment (for deployment)
    port = int(os.environ.get("PORT", 5000))

    # run flask app
    app.run(host="0.0.0.0", port=port)