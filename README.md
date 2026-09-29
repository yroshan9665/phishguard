# AI-Based Phishing Website Detection System

A production-ready B.Sc. Computer Science final-year project built with Flask, PostgreSQL, Scikit-learn, Chart.js, and ReportLab.

## Features

- **URL Analysis** — 15 features: URL length, HTTPS, IP usage, domain age, SSL, subdomains, special characters, suspicious keywords, login forms, external links, hidden elements, redirect count, suspicious JS, and more
- **ML Classification** — Random Forest classifier predicts Safe / Suspicious / Phishing with confidence % and risk score (0–100)
- **Analytics Dashboard** — Chart.js charts: threat distribution, risk trend, daily scans
- **PDF Reports** — Downloadable security reports with ReportLab
- **Admin Panel** — User management, global analytics, scan history
- **Secure Auth** — Flask-Login + Bcrypt password hashing + CSRF protection

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Flask 3.0 |
| Database | PostgreSQL + SQLAlchemy |
| ML | Scikit-learn (Random Forest), Pandas, NumPy |
| Frontend | Bootstrap 5, Chart.js, Bootstrap Icons |
| PDF | ReportLab |
| Scraping | BeautifulSoup, Requests |
| WHOIS | python-whois |

## Project Structure

```
mini project/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # SQLAlchemy models (User, ScanResult)
│   ├── auth/routes.py       # Login, Register, Logout
│   ├── scanner/routes.py    # URL scan + PDF report
│   ├── dashboard/routes.py  # User dashboard + chart API
│   ├── admin/routes.py      # Admin panel
│   ├── ml/
│   │   ├── feature_extractor.py  # 15-feature URL extractor
│   │   ├── train_model.py        # Model training script
│   │   └── predictor.py          # Prediction wrapper
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/{login,register}.html
│   │   ├── dashboard/index.html
│   │   ├── scanner/{scan,result}.html
│   │   └── admin/index.html
│   └── static/
│       ├── css/style.css
│       └── js/main.js
├── config.py
├── run.py
├── seed_admin.py
├── requirements.txt
└── .env
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure PostgreSQL
Create a database named `phishing_db`:
```sql
CREATE DATABASE phishing_db;
```
Update `.env` with your credentials:
```
SECRET_KEY=your-very-secure-secret-key
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/phishing_db
```

### 3. Train the ML Model
```bash
python -m app.ml.train_model
```

### 4. Create Admin User
```bash
python seed_admin.py
```

### 5. Run the Application
```bash
python run.py
```
Visit: [http://localhost:5000](http://localhost:5000)

## Netlify Deployment

1. Connect your repository to [Netlify](https://app.netlify.com).
2. Netlify will automatically detect `netlify.toml` and configure the Python serverless function in `netlify/functions/app.py`.
3. Set the following Environment Variables in the Netlify Dashboard (**Site settings > Environment variables**):
   - `SECRET_KEY` = (A secure random secret)
   - `DATABASE_URL` = (Your external PostgreSQL connection string, e.g. from Supabase / Neon / ElephantSQL)
   - `ADMIN_USERNAME` = `admin`
   - `ADMIN_EMAIL` = `admin@phishguard.ai`
   - `ADMIN_PASSWORD` = `YourSecurePassword`
4. Deploy the site!

## Routes

| Route | Description |
|-------|-------------|
| `/` | Instant URL Scanner (public, no login required) |
| `/scanner/scan` | Submit URL for analysis (public) |
| `/scanner/result/<id>` | View scan verdict & 15 signals (public) |
| `/scanner/report/<id>/pdf` | Download forensic PDF report (sign-in required) |
| `/auth/login` | User login |
| `/auth/register` | User registration |
| `/dashboard/` | User analytics dashboard (authenticated) |
| `/admin/` | Admin console (admin only) |

## ML Model Details

- **Algorithm**: Random Forest (200 trees, max_depth=12)
- **Features**: 15 URL + page-level signals
- **Labels**: Safe, Suspicious, Phishing
- **Training data**: 3000 synthetic samples (balanced classes)
- **Risk Score**: Weighted phishing (80%) + suspicious (40%) probability

## Security Notes

- Passwords hashed with Bcrypt (cost factor 12)
- CSRF protection on all POST forms
- Admin-only routes protected by decorator
- Session managed by Flask-Login
