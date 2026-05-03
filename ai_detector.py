from sklearn.ensemble import IsolationForest
import pandas as pd


def detect_anomaly(df):

    try:

        if df is None or len(df) == 0:
            return []

        # Convert login status to numeric feature
        df["status_code"] = df["status"].apply(
            lambda x: 1 if x == "FAILED" else 0
        )

        # Feature engineering

        # count failed attempts per IP
        df["ip_attempts"] = df.groupby("ip")["status_code"].transform("sum")

        # count login attempts per user
        df["user_attempts"] = df.groupby("user")["status_code"].transform("sum")

        # extract hour feature if time exists
        try:
            df["hour"] = pd.to_datetime(df["time"]).dt.hour
        except:
            df["hour"] = 0

        # features for ML model
        features = df[["status_code", "ip_attempts", "user_attempts", "hour"]]

        # Isolation Forest model
        model = IsolationForest(
        contamination=0.1,
        n_estimators=100,
        max_samples=256,
        random_state=42)

        model.fit(features)

        df["anomaly"] = model.predict(features)

        anomalies = df[df["anomaly"] == -1]

        return anomalies

    except Exception as e:

        print("[AI DETECTOR ERROR]", e)

        return []