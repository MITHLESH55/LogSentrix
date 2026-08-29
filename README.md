![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-Web_App-black)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)
![AI](https://img.shields.io/badge/AI-Threat_Detection-red)


# LogSentrix

AI-powered cybersecurity log monitoring and threat detection platform with real-time anomaly detection, anomaly analysis, and attack visualization dashboard.

---

🌐 **[Live Demo](https://mithleshyadav.pythonanywhere.com/)**  
💻 **[GitHub Repository](https://github.com/MITHLESH55/LogSentrix)**

## Features

- Real-time log monitoring
- AI-based anomaly detection
- Threat intelligence integration
- Attack visualization dashboard
- SQLite audit logging
- IP reputation lookup
- Email alert system
- Live threat analysis

---

## Tech Stack

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript

---


## 🏗 System Architecture

```text
                    ┌─────────────────────┐
                    │      User/Admin     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Flask Web Server  │
                    │      (app.py)       │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
 ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
 │ Log Generator  │  │ Threat Engine  │  │ Alert System   │
 │log_generator.py│  │ detector.py    │  │ alerts.py      │
 └────────┬───────┘  └────────┬───────┘  └────────┬───────┘
          │                   │                   │
          ▼                   ▼                   ▼
 ┌────────────────────────────────────────────────────────┐
 │                 AI Detection Layer                     │
 │     anomaly detection + suspicious pattern analysis   │
 └─────────────────────────┬──────────────────────────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ SQLite Database     │
                │ database.py         │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Dashboard & Graphs  │
                │ templates + static  │
                └─────────────────────┘
```


## 📁 Project Structure

```text
LogSentrix/
│
├── app.py
├── requirements.txt
├── .env.example
├── README.md
│
├── database/
├── logs/
├── static/
├── templates/
│
├── ai_detector.py
├── alerts.py
├── detector.py
├── parser.py
├── database.py
├── diagnose_logs.py
├── ip_lookup.py
├── log_generator.py
│
├── test_mail.py
├── test_realtime_dashboard.py
├── test_sqlite_database.py
└── test_threat_intelligence.py
```



---

## Future Enhancements

- Machine learning based threat prediction
- Cloud deployment support
- Advanced SIEM integration
- Real-time notification system
- Interactive analytics dashboard
- Multi-user authentication


## 👨‍💻 Author

Mithlesh Yadav  
BTech CSE | Symbiosis Institute of Technology
