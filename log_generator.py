import random
import time
from datetime import datetime

LOG_FILE = "logs/server.log"

users = ["admin", "root", "guest", "test"]
ips = [
    "192.168.1.15",
    "192.168.1.16",
    "192.168.1.20",
    "45.12.34.56",
    "103.25.44.90",
    "66.249.66.1",
    "95.161.229.130",
    "123.125.114.144",
    "106.51.78.20",
    "176.9.0.1"
]

statuses = ["SUCCESS", "FAILED"]


def generate_log():

    user = random.choice(users)
    ip = random.choice(ips)

    # simulate attacks (more failures)
    status = random.choices(
        statuses,
        weights=[30, 70]
    )[0]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log = f"{timestamp} LOGIN {status} user={user} ip={ip}\n"

    with open(LOG_FILE, "a") as f:
        f.write(log)

    print("Generated log:", log.strip())


while True:

    generate_log()

    time.sleep(3)