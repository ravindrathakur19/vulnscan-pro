# VulnScan Pro - Web App

Advanced Web Vulnerability Scanner with live terminal output.

## Local Setup

```bash
pip install -r requirements.txt
python app.py
# Open http://localhost:5000
```

## Deploy to Render.com (Free)

1. GitHub pe push karo (app.py, scanner_core.py, templates/, requirements.txt, Procfile)
2. render.com pe New Web Service create karo
3. Repo connect karo
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn --worker-class eventlet -w 1 app:app --bind 0.0.0.0:$PORT`
6. Deploy!

## Deploy to Railway.app (Free)

1. railway.app pe New Project
2. GitHub repo connect karo
3. Auto-detect karega — Deploy!

## Files Structure

```
webapp/
├── app.py              # Flask + SocketIO server
├── scanner_core.py     # Scanner logic (from scanner_v3.py)
├── requirements.txt    # Dependencies
├── Procfile            # For Render/Railway
├── reports/            # Generated reports (auto-created)
└── templates/
    └── index.html      # Frontend UI
```
