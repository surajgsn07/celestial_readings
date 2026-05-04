# Hostinger ₹149 Plan — Project Compatibility Analysis

## Current Project State
Your Flask app currently has **Docker-based** setup files (`Dockerfile`, `docker-compose.yml`, `.dockerignore`) and uses PostgreSQL (via Supabase). The core Python code (`app.py`, `models.py`, `config.py`, templates, static files) is already platform-agnostic.

## What Works As-Is (No Changes Needed)

| File | Status | Notes |
| :--- | :--- | :--- |
| `app.py` | ✅ Ready | All routes, logic, APIs — no change |
| `models.py` | ✅ Ready | SQLAlchemy models work anywhere |
| `config.py` | ✅ Ready | Reads from `.env` — platform-independent |
| `.env` | ✅ Ready | Just update values for production |
| `templates/` | ✅ Ready | All 11 HTML templates — no change |
| `static/css/` | ✅ Ready | All styles — no change |
| `static/js/` | ✅ Ready | All 4 JS files — no change |
| **Database** | ✅ Ready | Supabase (external) — works from anywhere |

## What Needs to Change (3 Things Only)

### 1. [NEW] `passenger_wsgi.py` — Entry point for Hostinger
Hostinger uses Passenger to serve Python apps. This 1-line file tells Passenger where your Flask app is.

### 2. [MODIFY] `requirements.txt` — Remove `gunicorn`
Gunicorn is a Linux server used with Docker/VPS. Hostinger uses Passenger instead, so gunicorn is not needed (and won't work on shared hosting).

### 3. [KEEP BUT IGNORE] Docker files
`Dockerfile`, `docker-compose.yml`, `.dockerignore` — keep them in the repo (useful if you ever move to VPS later), but they won't be used on Hostinger.

---

## How to Run Locally WITHOUT Docker

### Option A: Direct Python (Simplest)
```bash
# 1. Create virtual environment (one-time)
python -m venv venv

# 2. Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```
Then open `http://localhost:5000` in your browser. That's it!

> [!NOTE]
> For local development, you'll need a local PostgreSQL database OR you can use your Supabase URL directly in `.env`. Using Supabase even locally is the easiest approach — no need to install PostgreSQL on your machine.

### Option B: Keep Docker (Optional)
If you still want Docker locally for convenience, `docker compose up --build` still works. Both approaches are fine — Docker for local dev, Passenger for Hostinger production.

---

## Hostinger Deployment Steps

### Step 1: Buy the ₹149 Premium Plan
- Go to hostinger.in → Premium Web Hosting → Buy

### Step 2: Enable SSH Access
- hPanel → Advanced → SSH Access → Enable

### Step 3: SSH into Server
```bash
ssh u123456789@your-server.hostinger.com -p 65002
```

### Step 4: Set Up Python Environment
```bash
# Navigate to your website's directory
cd ~/domains/yourdomain.com/public_html

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upload your project files (via Git or File Manager)
# Then install dependencies:
pip install -r requirements.txt
```

### Step 5: Configure `.env` on Server
```env
SECRET_KEY=a-very-strong-random-secret-key-here
FLASK_ENV=production
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres
UPI_ID=yourclient@okicici
UPI_NAME=Tinkerbell Chronicles
WHATSAPP_NUMBER=919876543210
```

### Step 6: Set Up Python App in hPanel
- hPanel → Website → Advanced → Python
- Set Python version: 3.11
- Set Application root: `/domains/yourdomain.com/public_html`
- Set Application startup file: `passenger_wsgi.py`
- Click "Create"

### Step 7: Done! 🎉
Visit your domain to see the live site.

## Verification Plan
- Visit the homepage to check it loads
- Test the booking flow end-to-end
- Test admin login at `/admin/login`
- Test UPI payment proof submission
- Test admin payment verification
