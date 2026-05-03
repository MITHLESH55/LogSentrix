def get_severity(attempts):

    if attempts > 100:
        return "CRITICAL"
    elif attempts > 50:
        return "HIGH"
    elif attempts > 20:
        return "MEDIUM"
    else:
        return "LOW"


def calculate_risk(attempts):
    """Calculate risk score from attempt count.
    Provides a dynamic scale so percentages vary properly.
    """
    try:
        a = int(attempts)
        if a <= 5:
            score = 15 + (a * 5)
        elif a <= 20:
            score = 40 + (a - 5) * 2
        elif a <= 50:
            score = 70 + (a - 20) * 0.5
        elif a <= 100:
            score = 85 + (a - 50) * 0.16
        elif a <= 200:
            score = 93 + (a - 100) * 0.05
        else:
            score = 98 + min(2, (a - 200) * 0.01)
        return int(score)
    except (TypeError, ValueError):
        return 0


def detect_bruteforce(df):

    alerts = []

    failed_logs = df[df["status"] == "FAILED"]

    ip_counts = failed_logs["ip"].value_counts()

    for ip, count in ip_counts.items():

        attempts = int(count)

        severity = get_severity(attempts)

        # trigger alert only after minimum suspicious attempts
        if attempts >= 3:
            risk = calculate_risk(attempts)

            alerts.append({
                "ip": ip,
                "type": "Brute Force Attack",
                "attempts": attempts,
                "severity": severity,
                "risk": risk
            })

    return alerts


def detect_password_spray(df):

    alerts = []

    failed_logs = df[df["status"] == "FAILED"]

    # same IP attacking multiple users
    grouped = failed_logs.groupby("ip")["user"].nunique()

    for ip, user_count in grouped.items():

        if user_count >= 5:
            risk = calculate_risk(user_count)

            alerts.append({
                "ip": ip,
                "type": "Password Spray",
                "attempts": int(user_count),
                "severity": "HIGH",
                "risk": risk
            })

    return alerts


def detect_suspicious_login(df):

    alerts = []

    # detect login attempts from many IPs for the same user
    grouped = df.groupby("user")["ip"].nunique()

    for user, ip_count in grouped.items():

        if ip_count >= 5:
            risk = calculate_risk(ip_count)

            alerts.append({
                "ip": "Multiple",
                "type": "Suspicious Login Behavior",
                "attempts": int(ip_count),
                "severity": "MEDIUM",
                "risk": risk
            })

    return alerts


def detect_threat(df):

    alerts = []

    if df is None or len(df) == 0:
        return alerts

    try:

        # brute force detection
        alerts.extend(detect_bruteforce(df))

        # password spray detection
        alerts.extend(detect_password_spray(df))

        # suspicious login behaviour
        alerts.extend(detect_suspicious_login(df))

    except Exception as e:

        print("[DETECTION ERROR]", e)

    return alerts