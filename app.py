"""
Advanced Web Vulnerability Scanner - Web App
Flask + SocketIO for live terminal output
"""
import os
import sys
import json
import uuid
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, abort
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'vuln-scanner-secret-2024')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store active scans and results
active_scans = {}   # scan_id -> thread
scan_results = {}   # scan_id -> findings list
scan_reports = {}   # scan_id -> html report path

# ── Import scanner core ───────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

try:
    from scanner_core import VulnScanner, generate_html_report, generate_json_report
except ImportError:
    print("[!] scanner_core.py not found next to app.py")
    sys.exit(1)


# ── Routes ────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/scan', methods=['POST'])
def start_scan():
    data = request.get_json()
    target = data.get('url', '').strip()
    full_scan = data.get('full_scan', True)
    threads = int(data.get('threads', 10))
    timeout = int(data.get('timeout', 5))

    if not target:
        return jsonify({'error': 'URL is required'}), 400

    if not target.startswith(('http://', 'https://')):
        target = 'https://' + target

    scan_id = str(uuid.uuid4())[:8]
    scan_results[scan_id] = []

    def run_scan():
        try:
            socketio.emit('log', {
                'scan_id': scan_id,
                'level': 'INFO',
                'msg': f'Starting scan on {target}...',
                'ts': datetime.now().strftime('%H:%M:%S')
            })

            scanner = VulnScanner(
                target=target,
                threads=threads,
                timeout=timeout,
                verbose=False,
                crawl=full_scan,
                socket_callback=lambda level, msg: socketio.emit('log', {
                    'scan_id': scan_id,
                    'level': level,
                    'msg': msg,
                    'ts': datetime.now().strftime('%H:%M:%S')
                }),
                finding_callback=lambda f: socketio.emit('finding', {
                    'scan_id': scan_id,
                    'finding': f
                })
            )

            findings = scanner.run(full_scan=full_scan)
            scan_results[scan_id] = findings

            # Generate reports
            os.makedirs('reports', exist_ok=True)
            html_path = generate_html_report(findings, target, 'reports')
            json_path = generate_json_report(findings, target, 'reports')
            scan_reports[scan_id] = {
                'html': html_path,
                'json': json_path
            }

            socketio.emit('scan_complete', {
                'scan_id': scan_id,
                'total': len(findings),
                'critical': sum(1 for f in findings if f['severity'] == 'CRITICAL'),
                'high':     sum(1 for f in findings if f['severity'] == 'HIGH'),
                'medium':   sum(1 for f in findings if f['severity'] == 'MEDIUM'),
                'low':      sum(1 for f in findings if f['severity'] == 'LOW'),
                'html_report': f'/report/{scan_id}/html',
                'json_report': f'/report/{scan_id}/json',
            })

        except Exception as e:
            socketio.emit('scan_error', {
                'scan_id': scan_id,
                'error': str(e)
            })

    t = threading.Thread(target=run_scan, daemon=True)
    active_scans[scan_id] = t
    t.start()

    return jsonify({'scan_id': scan_id, 'status': 'started'})


@app.route('/report/<scan_id>/<fmt>')
def download_report(scan_id, fmt):
    if scan_id not in scan_reports:
        abort(404)
    path = scan_reports[scan_id].get(fmt)
    if not path or not os.path.exists(path):
        abort(404)
    mimetype = 'text/html' if fmt == 'html' else 'application/json'
    return send_file(path, mimetype=mimetype, as_attachment=True,
                     download_name=f'vuln_report_{scan_id}.{fmt}')


@app.route('/api/status/<scan_id>')
def scan_status(scan_id):
    findings = scan_results.get(scan_id, [])
    is_done = scan_id in scan_reports
    return jsonify({
        'scan_id': scan_id,
        'done': is_done,
        'findings_count': len(findings),
        'findings': findings
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
