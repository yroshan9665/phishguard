"""
Feature extraction module: pulls 15 signals from a URL for ML prediction.
"""
import re
import ssl
import socket
import requests
import whois
from urllib.parse import urlparse
from datetime import datetime
from bs4 import BeautifulSoup

SUSPICIOUS_KEYWORDS = ['login', 'verify', 'update', 'secure', 'account',
                       'banking', 'confirm', 'paypal', 'ebay', 'amazon',
                       'password', 'signin', 'wallet', 'free', 'lucky']

def extract_features(url: str) -> dict:
    """Return a dict of features extracted from the given URL."""
    features = {}
    parsed = urlparse(url if url.startswith('http') else 'http://' + url)
    domain = parsed.netloc or parsed.path

    # 1. URL length
    features['url_length'] = len(url)

    # 2. HTTPS
    features['has_https'] = int(parsed.scheme == 'https')

    # 3. IP address used as domain
    ip_pattern = re.compile(r'^\d{1,3}(\.\d{1,3}){3}$')
    features['has_ip'] = int(bool(ip_pattern.match(domain.split(':')[0])))

    # 4. Subdomain count
    parts = domain.replace('www.', '').split('.')
    features['subdomain_count'] = max(0, len(parts) - 2)

    # 5. Special character count
    features['special_char_count'] = len(re.findall(r'[@\-_~]', url))

    # 6. Suspicious keywords in URL
    url_lower = url.lower()
    features['suspicious_keywords'] = sum(1 for k in SUSPICIOUS_KEYWORDS if k in url_lower)

    # 7. Number of dots
    features['dot_count'] = url.count('.')

    # 8. URL contains '@'
    features['has_at_symbol'] = int('@' in url)

    # 9. Domain age (days); -1 if unavailable
    features['domain_age_days'] = _get_domain_age(domain)

    # 10. SSL valid
    features['ssl_valid'] = _check_ssl(domain)

    # 11–15: Page-level features (requires HTTP fetch)
    page_features = _fetch_page_features(url)
    features.update(page_features)

    return features


def _get_domain_age(domain: str) -> int:
    try:
        w = whois.whois(domain.split(':')[0])
        creation = w.creation_date
        if isinstance(creation, list):
            creation = creation[0]
        if creation:
            return (datetime.utcnow() - creation).days
    except Exception:
        pass
    return -1


def _check_ssl(domain: str) -> int:
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain.split(':')[0]) as s:
            s.settimeout(5)
            s.connect((domain.split(':')[0], 443))
        return 1
    except Exception:
        return 0


def _fetch_page_features(url: str) -> dict:
    defaults = {
        'has_login_form': 0,
        'external_links': 0,
        'hidden_elements': 0,
        'redirect_count': 0,
        'has_suspicious_js': 0,
    }
    try:
        resp = requests.get(
            url if url.startswith('http') else 'http://' + url,
            timeout=8, allow_redirects=True,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        defaults['redirect_count'] = len(resp.history)
        soup = BeautifulSoup(resp.text, 'html.parser')
        parsed = urlparse(resp.url)
        base_domain = parsed.netloc

        # Login form detection
        forms = soup.find_all('form')
        defaults['has_login_form'] = int(any(
            inp.get('type') in ['password', 'email'] for f in forms for inp in f.find_all('input')
        ))

        # External links
        links = soup.find_all('a', href=True)
        defaults['external_links'] = sum(
            1 for a in links if base_domain and base_domain not in a['href']
            and a['href'].startswith('http')
        )

        # Hidden elements
        defaults['hidden_elements'] = len(soup.find_all(style=re.compile(r'display\s*:\s*none')))

        # Suspicious JS
        scripts = ' '.join(s.string or '' for s in soup.find_all('script'))
        suspicious_js = ['eval(', 'unescape(', 'fromCharCode', 'document.write(']
        defaults['has_suspicious_js'] = int(any(p in scripts for p in suspicious_js))

    except Exception:
        pass
    return defaults


def features_to_vector(features: dict) -> list:
    """Return features as an ordered list matching the training column order."""
    cols = [
        'url_length', 'has_https', 'has_ip', 'subdomain_count',
        'special_char_count', 'suspicious_keywords', 'dot_count',
        'has_at_symbol', 'domain_age_days', 'ssl_valid',
        'has_login_form', 'external_links', 'hidden_elements',
        'redirect_count', 'has_suspicious_js'
    ]
    return [features.get(c, 0) for c in cols]
