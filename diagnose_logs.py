from parser import parse_logs
from pathlib import Path

LOG_FILE = Path("logs/server.log")
df = parse_logs(LOG_FILE)
print(f"Log File: {LOG_FILE.absolute()}")
print(f"Records found: {len(df)}")
if len(df) > 0:
    print(df.head())
else:
    print("DataFrame is empty!")
