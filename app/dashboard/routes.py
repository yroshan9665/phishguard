from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import ScanResult

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def index():
    recent = (ScanResult.query
              .filter_by(user_id=current_user.id)
              .order_by(ScanResult.scanned_at.desc())
              .limit(10).all())
    stats = _user_stats(current_user.id)
    return render_template('dashboard/index.html', recent=recent, stats=stats)


@dashboard_bp.route('/api/chart-data')
@login_required
def chart_data():
    uid = current_user.id

    dist = (db.session.query(ScanResult.prediction, func.count(ScanResult.id))
            .filter_by(user_id=uid)
            .group_by(ScanResult.prediction).all())
    dist_dict = {row[0]: row[1] for row in dist}

    trend_docs = (ScanResult.query
                  .filter_by(user_id=uid)
                  .order_by(ScanResult.scanned_at.desc())
                  .limit(14).all())
    trend_docs.reverse()
    trend_labels = [d.scanned_at.strftime('%m/%d') for d in trend_docs]
    trend_scores = [d.risk_score for d in trend_docs]

    today = datetime.utcnow().date()
    daily = {}
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day)
        day_end   = day_start + timedelta(days=1)
        count = (ScanResult.query
                 .filter_by(user_id=uid)
                 .filter(ScanResult.scanned_at >= day_start,
                         ScanResult.scanned_at < day_end)
                 .count())
        daily[day.strftime('%a')] = count

    return jsonify({
        'distribution': {
            'labels': ['Safe', 'Suspicious', 'Phishing'],
            'data': [dist_dict.get('Safe', 0),
                     dist_dict.get('Suspicious', 0),
                     dist_dict.get('Phishing', 0)],
        },
        'risk_trend':  {'labels': trend_labels, 'data': trend_scores},
        'daily_scans': {'labels': list(daily.keys()), 'data': list(daily.values())},
    })


def _user_stats(user_id):
    base = ScanResult.query.filter_by(user_id=user_id)
    return {
        'total':      base.count(),
        'phishing':   base.filter_by(prediction='Phishing').count(),
        'suspicious': base.filter_by(prediction='Suspicious').count(),
        'safe':       base.filter_by(prediction='Safe').count(),
    }
