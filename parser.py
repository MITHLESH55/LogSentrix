import pandas as pd
import re


def parse_logs(file):

    records = []

    try:

        with open(file, "r") as f:

            for line in f:

                line = line.strip()

                # Example log format
                # 2024-04-10 10:15:23 LOGIN FAILED user=admin ip=192.168.1.5

                pattern = r'(\S+\s+\S+)\s+LOGIN\s+(\S+)\s+user=(\S+)\s+ip=(\S+)'

                match = re.search(pattern, line)

                if match:

                    records.append({
                        "time": match.group(1),
                        "status": match.group(2),
                        "user": match.group(3),
                        "ip": match.group(4)
                    })

    except FileNotFoundError:
        print("[ERROR] Log file not found:", file)

    except Exception as e:
        print("[ERROR] Parsing logs:", e)

    # Create dataframe
    df = pd.DataFrame(records)

    # If empty return structured dataframe
    if df.empty:
        return pd.DataFrame(columns=["time", "status", "user", "ip"])

    # Convert timestamp
    try:
        df["time"] = pd.to_datetime(df["time"])
    except:
        pass

    # Feature engineering for AI / analytics

    # Failed login flag
    df["failed_flag"] = df["status"].apply(lambda x: 1 if x == "FAILED" else 0)

    # Hour extraction for attack trend
    try:
        df["hour"] = df["time"].dt.hour
    except:
        df["hour"] = None

    # Count attempts per IP (useful for anomaly detection)
    ip_counts = df["ip"].value_counts()

    df["ip_attempts"] = df["ip"].map(ip_counts)

    # --------------------------------
    # Limit records for performance
    # --------------------------------
    if len(df) > 1000:
        df = df.tail(1000)

    return df