import re, math
from datetime import datetime
from io import BytesIO
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, send_file)
from flask_login import login_required, current_user
from app import db
from app.models import ScanResult
from app.ml.predictor import predict

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                Table, TableStyle)
from reportlab.graphics.shapes import Drawing, String, Line

scanner_bp = Blueprint('scanner', __name__, url_prefix='/scanner')

URL_REGEX = re.compile(r'^(https?://)?([\w\-]+\.)+[\w]{2,}(/.*)?$', re.IGNORECASE)

C_BG     = colors.HexColor('#0d0d2b')
C_CARD   = colors.HexColor('#12122e')
C_ACCENT = colors.HexColor('#7c6fff')
C_WHITE  = colors.white
C_MUTED  = colors.HexColor('#8888aa')
C_SAFE   = colors.HexColor('#10b981')
C_WARN   = colors.HexColor('#f59e0b')
C_DANGER = colors.HexColor('#ef4444')
C_ROW1   = colors.HexColor('#0f0f28')
C_ROW2   = colors.HexColor('#0b0b1e')
C_BORDER = colors.HexColor('#1e1e40')
C_CYAN   = colors.HexColor('#06b6d4')

def _vc(pred):
    return {'Safe': C_SAFE, 'Suspicious': C_WARN, 'Phishing': C_DANGER}.get(pred, C_MUTED)


@scanner_bp.route('/scan', methods=['GET', 'POST'])
@login_required
def scan():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if not url or not URL_REGEX.match(url):
            flash('Please enter a valid URL.', 'danger')
            return redirect(url_for('scanner.scan'))
        try:
            result = predict(url)
            scan_result = ScanResult(
                user_id    = current_user.id,
                url        = url,
                prediction = result['prediction'],
                confidence = result['confidence'],
                risk_score = result['risk_score'],
                features   = result['features'],
            )
            db.session.add(scan_result)
            db.session.commit()
            return redirect(url_for('scanner.result', scan_id=scan_result.id))
        except FileNotFoundError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Scan failed: {e}', 'danger')
        return redirect(url_for('scanner.scan'))
    return render_template('scanner/scan.html')


@scanner_bp.route('/result/<int:scan_id>')
@login_required
def result(scan_id):
    scan = ScanResult.query.get_or_404(scan_id)
    if scan.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
    return render_template('scanner/result.html', scan=scan)


@scanner_bp.route('/report/<int:scan_id>/pdf')
@login_required
def download_report(scan_id):
    scan = ScanResult.query.get_or_404(scan_id)
    if scan.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
    buf = BytesIO()
    _build_pdf(scan, buf)
    buf.seek(0)
    return send_file(buf, as_attachment=True,
                     download_name=f'PhishGuard_Report_{scan_id}.pdf',
                     mimetype='application/pdf')


# ── PDF helpers ────────────────────────────────────────────────────
def _make_header_footer(scan):
    W, H = A4
    vc   = _vc(scan.prediction)
    def _draw(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(C_BG)
        canvas.rect(0, H - 3.8*cm, W, 3.8*cm, fill=1, stroke=0)
        canvas.setFillColor(C_ACCENT)
        canvas.rect(0, H - 3.8*cm, W, 2.5*mm, fill=1, stroke=0)
        canvas.setFillColor(C_ACCENT)
        canvas.circle(2.4*cm, H - 1.9*cm, 0.52*cm, fill=1, stroke=0)
        canvas.setFillColor(C_WHITE)
        canvas.setFont('Helvetica-Bold', 9)
        canvas.drawCentredString(2.4*cm, H - 1.94*cm, 'PG')
        canvas.setFillColor(C_WHITE)
        canvas.setFont('Helvetica-Bold', 17)
        canvas.drawString(3.3*cm, H - 1.65*cm, 'PhishGuard')
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(C_MUTED)
        canvas.drawString(3.3*cm, H - 2.1*cm, 'Security Analysis Report')
        canvas.setFillColor(C_MUTED)
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(W - 1.8*cm, H - 1.62*cm, f'Scan ID: #{scan.id}')
        canvas.drawRightString(W - 1.8*cm, H - 2.1*cm,
                               scan.scanned_at.strftime('%d %b %Y  %H:%M UTC'))
        vx, vy, pill_w = W - 1.8*cm, H - 3.0*cm, 2.4*cm
        canvas.setFillColor(vc)
        canvas.roundRect(vx - pill_w, vy, pill_w, 0.55*cm, 6, fill=1, stroke=0)
        canvas.setFillColor(C_WHITE)
        canvas.setFont('Helvetica-Bold', 9)
        canvas.drawCentredString(vx - pill_w/2, vy + 0.14*cm, scan.prediction.upper())
        canvas.setFillColor(C_BG)
        canvas.rect(0, 0, W, 1.1*cm, fill=1, stroke=0)
        canvas.setFillColor(C_MUTED)
        canvas.setFont('Helvetica', 7.5)
        canvas.drawString(1.8*cm, 0.42*cm, 'PhishGuard \u00b7 Confidential Security Report')
        canvas.drawRightString(W - 1.8*cm, 0.42*cm,
                               f'Page {doc.page} \u00b7 {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}')
        canvas.restoreState()
    return _draw


def _risk_gauge(score, color):
    d = Drawing(5.5*cm, 3.2*cm)
    cx, cy, r = 2.75*cm, 0.6*cm, 2.0*cm
    for deg in range(0, 181, 3):
        a = math.radians(deg)
        ln = Line(cx+(r-7)*math.cos(a), cy+(r-7)*math.sin(a),
                  cx+r*math.cos(a),     cy+r*math.sin(a))
        ln.strokeColor = colors.HexColor('#1a1a3a'); ln.strokeWidth = 2.5; d.add(ln)
    for deg in range(0, int(score*1.8), 3):
        a = math.radians(deg)
        ln = Line(cx+(r-7)*math.cos(a), cy+(r-7)*math.sin(a),
                  cx+r*math.cos(a),     cy+r*math.sin(a))
        ln.strokeColor = color; ln.strokeWidth = 2.5; d.add(ln)
    d.add(String(cx, cy+3,  str(score), fontName='Helvetica-Bold', fontSize=17,
                 fillColor=color, textAnchor='middle'))
    d.add(String(cx, cy-10, 'RISK SCORE', fontName='Helvetica', fontSize=6,
                 fillColor=C_MUTED, textAnchor='middle'))
    return d


def _build_pdf(scan, dest):
    W, H = A4
    LM, RM = 1.8*cm, 1.8*cm
    TW = W - LM - RM
    cb = _make_header_footer(scan)
    vc = _vc(scan.prediction)
    styles = getSampleStyleSheet()
    story  = [Spacer(1, 3.6*cm)]
    N  = ParagraphStyle('n',  parent=styles['Normal'], fontSize=9, wordWrap='LTR', splitLongWords=1)
    NW = ParagraphStyle('nw', parent=styles['Normal'], fontSize=9, wordWrap='CJK', splitLongWords=1)
    SEC = ParagraphStyle('sec', fontName='Helvetica-Bold', fontSize=11,
                         textColor=C_ACCENT, leading=16, spaceBefore=8, spaceAfter=4)

    vbg = {'Safe':'#0a2e1e','Suspicious':'#2e1e00','Phishing':'#2e0a0a'}.get(scan.prediction,'#111')
    banner = Table([[
        Paragraph(f'<font color="{vc.hexval()}" size="18"><b>{scan.prediction.upper()}</b></font>', N),
        Paragraph(f'<font color="{vc.hexval()}" size="16"><b>{scan.confidence}%</b></font><br/><font color="#8888aa" size="8">Confidence</font>', N),
        Paragraph(f'<font color="{vc.hexval()}" size="16"><b>{scan.risk_score}/100</b></font><br/><font color="#8888aa" size="8">Risk Score</font>', N),
    ]], colWidths=[TW-6.0*cm, 3.0*cm, 3.0*cm])
    banner.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),colors.HexColor(vbg)),
        ('BOX',(0,0),(-1,-1),1.5,vc), ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('ALIGN',(1,0),(-1,-1),'CENTER'),
        ('TOPPADDING',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),12),
        ('LEFTPADDING',(0,0),(0,-1),14),
    ]))
    story.append(banner); story.append(Spacer(1, 0.4*cm))

    url_text = scan.url
    if len(url_text) > 70:
        url_text = ' '.join([url_text[i:i+60] for i in range(0, len(url_text), 60)])
    info = Table([
        [Paragraph('<font color="#7c6fff"><b>Target URL</b></font>', N),
         Paragraph(f'<font color="#e0e0ff">{url_text}</font>', NW)],
        [Paragraph('<font color="#7c6fff"><b>Scanned By</b></font>', N),
         Paragraph(f'<font color="#e0e0ff">{scan.user.username}</font>', N)],
        [Paragraph('<font color="#7c6fff"><b>Timestamp</b></font>', N),
         Paragraph(f'<font color="#e0e0ff">{scan.scanned_at.strftime("%d %B %Y at %H:%M:%S UTC")}</font>', N)],
    ], colWidths=[3.2*cm, TW-3.2*cm])
    info.setStyle(TableStyle([
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[C_ROW1,C_ROW2,C_ROW1]),
        ('BOX',(0,0),(-1,-1),0.5,C_BORDER),('INNERGRID',(0,0),(-1,-1),0.3,C_BORDER),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))
    story.append(info); story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph('Risk Assessment', SEC))
    gauge = _risk_gauge(scan.risk_score, vc)
    level = 'LOW' if scan.risk_score < 30 else ('MEDIUM' if scan.risk_score < 60 else 'HIGH')
    GW, SW = 6.0*cm, TW-6.0*cm
    stats_inner = Table([
        [Paragraph(f'<font color="#8888aa" size="8">Verdict</font><br/><font color="{vc.hexval()}" size="12"><b>{scan.prediction}</b></font>', N)],
        [Paragraph(f'<font color="#8888aa" size="8">Confidence</font><br/><font color="#f0f0ff" size="12"><b>{scan.confidence}%</b></font>', N)],
        [Paragraph(f'<font color="#8888aa" size="8">Risk Level</font><br/><font color="{vc.hexval()}" size="10"><b>{level}</b></font>', N)],
    ], colWidths=[SW])
    stats_inner.setStyle(TableStyle([
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[C_ROW1,C_ROW2,C_ROW1]),
        ('BOX',(0,0),(-1,-1),0.5,C_BORDER),('INNERGRID',(0,0),(-1,-1),0.3,C_BORDER),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('LEFTPADDING',(0,0),(-1,-1),12),
    ]))
    gauge_row = Table([[gauge, stats_inner]], colWidths=[GW, SW])
    gauge_row.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('BACKGROUND',(0,0),(0,-1),C_CARD),
        ('BOX',(0,0),(0,-1),0.5,C_BORDER),
        ('TOPPADDING',(0,0),(0,-1),6),('BOTTOMPADDING',(0,0),(0,-1),6),
    ]))
    story.append(gauge_row); story.append(Spacer(1, 0.45*cm))

    story.append(Paragraph('Extracted Features', SEC))
    if scan.features:
        LABELS = {
            'url_length':'URL Length','has_https':'HTTPS Enabled','has_ip':'IP as Domain',
            'subdomain_count':'Subdomain Count','special_char_count':'Special Characters',
            'suspicious_keywords':'Suspicious Keywords','dot_count':'Dot Count',
            'has_at_symbol':'@ Symbol in URL','domain_age_days':'Domain Age (days)',
            'ssl_valid':'SSL Certificate Valid','has_login_form':'Login Form Present',
            'external_links':'External Links','hidden_elements':'Hidden Elements',
            'redirect_count':'Redirect Count','has_suspicious_js':'Suspicious JavaScript',
        }
        CHECKS = {
            'url_length':lambda v:v<75,'has_https':lambda v:v==1,'has_ip':lambda v:v==0,
            'subdomain_count':lambda v:v<=1,'special_char_count':lambda v:v<3,
            'suspicious_keywords':lambda v:v<2,'dot_count':lambda v:v<5,
            'has_at_symbol':lambda v:v==0,'domain_age_days':lambda v:v>180,
            'ssl_valid':lambda v:v==1,'has_login_form':lambda v:v==0,
            'external_links':lambda v:v<20,'hidden_elements':lambda v:v==0,
            'redirect_count':lambda v:v<2,'has_suspicious_js':lambda v:v==0,
        }
        FC1, FC2, FC3 = TW-5.2*cm, 2.2*cm, 3.0*cm
        rows = [[Paragraph(f'<font color="#fff"><b>{t}</b></font>', N)
                 for t in ['Feature','Value','Status']]]
        for k, v in scan.features.items():
            ok = CHECKS.get(k, lambda x: True)(v)
            sc = C_SAFE if ok else C_DANGER
            rows.append([
                Paragraph(f'<font color="#e0e0ff">{LABELS.get(k, k.replace("_"," ").title())}</font>', N),
                Paragraph(f'<font color="#a5b4fc"><b>{v}</b></font>', N),
                Paragraph(f'<font color="{sc.hexval()}"><b>{"OK" if ok else "Risk"}</b></font>', N),
            ])
        ft = Table(rows, colWidths=[FC1, FC2, FC3], splitByRow=1)
        ft.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),C_ACCENT),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[C_ROW1,C_ROW2]),
            ('BOX',(0,0),(-1,-1),0.5,C_BORDER),('INNERGRID',(0,0),(-1,-1),0.3,C_BORDER),
            ('FONTSIZE',(0,0),(-1,-1),9),
            ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
            ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),8),
            ('ALIGN',(1,0),(2,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ]))
        story.append(ft); story.append(Spacer(1, 0.45*cm))

    story.append(Paragraph('Security Recommendations', SEC))
    for rec in _recommendations(scan.prediction):
        is_crit = 'DO NOT' in rec
        story.append(Paragraph(
            f'<font color="{"#ef4444" if is_crit else "#e0e0e0"}">{"[!] " if is_crit else "  - "}{rec}</font>', N))
        story.append(Spacer(1, 3))
    story.append(Spacer(1, 0.3*cm))

    note = Table([[Paragraph(
        f'<font color="#8888aa" size="7.5">Generated by PhishGuard on '
        f'{datetime.utcnow().strftime("%d %B %Y at %H:%M UTC")}. '
        f'AI results are probabilistic — always verify through official channels.</font>', NW
    )]], colWidths=[TW])
    note.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),C_CARD),('BOX',(0,0),(-1,-1),0.5,C_BORDER),
        ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),
    ]))
    story.append(note)
    doc = SimpleDocTemplate(dest, pagesize=A4, rightMargin=RM, leftMargin=LM,
                            topMargin=0.5*cm, bottomMargin=1.6*cm, allowSplitting=1)
    doc.build(story, onFirstPage=cb, onLaterPages=cb)


def _recommendations(prediction):
    base = [
        'Always verify the website domain before entering credentials.',
        'Use a password manager to avoid entering passwords on unknown sites.',
        'Enable two-factor authentication on all important accounts.',
        'Keep your browser and antivirus software updated.',
    ]
    if prediction == 'Phishing':
        return ['DO NOT visit or interact with this website under any circumstances.',
                'Report this URL to Google Safe Browsing (safebrowsing.google.com).',
                'If credentials were entered, change them immediately.',
                'Run a full malware scan on your device.'] + base
    if prediction == 'Suspicious':
        return ['Exercise extreme caution when visiting this site.',
                'Do not enter passwords, credit card details, or personal information.',
                'Verify the site through official channels before proceeding.'] + base
    return ['This site appears safe based on current AI analysis.'] + base
