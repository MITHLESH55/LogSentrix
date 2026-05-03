import urllib.request
try:
    # Trigger the dashboard route (login might be required, but we just want to see if the log is written)
    # Actually, the app might be running on port 5000
    urllib.request.urlopen("http://127.0.0.1:5000/", timeout=2)
except Exception as e:
    print(f"Request failed (as expected if login required): {e}")
