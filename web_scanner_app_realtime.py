"""Web interface for The Red Room Security Scanner with Real-Time Progress."""

from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
import asyncio
import sys
import os
from datetime import datetime
import threading
import time
import structlog

logger = structlog.get_logger()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from redroom.agents.scanner.web_scanner import WebScanner
from redroom.database.scan_history import ScanHistoryDB
from redroom.reports.pdf_generator import PDFReportGenerator

app = Flask(__name__)
app.config['SECRET_KEY'] = 'redroom-secret-key-change-in-production'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize database and PDF generator
db = ScanHistoryDB()
pdf_generator = PDFReportGenerator()

# Store active scans
active_scans = {}

class ProgressCallback:
    """Callback handler for scan progress updates."""
    
    def __init__(self, sid):
        self.sid = sid
        self.total_tests = 70
        self.completed_tests = 0
        self.current_test = ""
        self.vulnerabilities_found = 0
    
    def update(self, test_name, status="running", vulnerability=None):
        """Update progress and emit to client."""
        if status == "completed":
            self.completed_tests += 1
        
        self.current_test = test_name
        
        if vulnerability:
            self.vulnerabilities_found += 1
        
        progress_data = {
            'current_test': test_name,
            'completed': self.completed_tests,
            'total': self.total_tests,
            'percentage': int((self.completed_tests / self.total_tests) * 100),
            'status': status,
            'vulnerabilities_found': self.vulnerabilities_found
        }
        
        if vulnerability:
            progress_data['vulnerability'] = vulnerability
        
        socketio.emit('scan_progress', progress_data, room=self.sid)

@app.route('/')
def index():
    return render_template('index_realtime.html')

@app.route('/health')
def health():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'service': 'redroom-scanner',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/history')
def history():
    """Scan history page."""
    return render_template('history.html')

@app.route('/api/scans', methods=['GET'])
def get_scans():
    """Get all scans."""
    limit = request.args.get('limit', 50, type=int)
    scans = db.get_all_scans(limit=limit)
    return jsonify({'scans': scans})

@app.route('/api/scans/<int:scan_id>', methods=['GET'])
def get_scan(scan_id):
    """Get specific scan."""
    scan = db.get_scan(scan_id)
    if scan:
        return jsonify({'scan': scan})
    return jsonify({'error': 'Scan not found'}), 404

@app.route('/api/scans/<int:scan_id>', methods=['DELETE'])
def delete_scan(scan_id):
    """Delete a scan."""
    if db.delete_scan(scan_id):
        return jsonify({'success': True})
    return jsonify({'error': 'Scan not found'}), 404

@app.route('/api/scans/compare', methods=['GET'])
def compare_scans():
    """Compare two scans."""
    scan_id1 = request.args.get('scan1', type=int)
    scan_id2 = request.args.get('scan2', type=int)
    
    if not scan_id1 or not scan_id2:
        return jsonify({'error': 'Both scan IDs required'}), 400
    
    comparison = db.compare_scans(scan_id1, scan_id2)
    if comparison:
        return jsonify({'comparison': comparison})
    return jsonify({'error': 'One or both scans not found'}), 404

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get overall statistics."""
    stats = db.get_statistics()
    return jsonify({'statistics': stats})

@app.route('/api/scans/target/<path:target_url>', methods=['GET'])
def get_scans_by_target(target_url):
    """Get scans for a specific target."""
    scans = db.get_scans_by_target(target_url)
    return jsonify({'scans': scans})

@app.route('/api/scans/<int:scan_id>/pdf', methods=['GET'])
def generate_pdf(scan_id):
    """Generate PDF report for a scan."""
    scan = db.get_scan(scan_id)
    if not scan:
        return jsonify({'error': 'Scan not found'}), 404
    
    try:
        # Prepare scan data
        scan_data = {
            'base_url': scan['target_url'],
            'vulnerabilities_found': scan['vulnerabilities_found'],
            'endpoints_found': scan['endpoints_found'],
            'vulnerabilities': scan['vulnerabilities'],
            'endpoints': scan['endpoints']
        }
        
        # Generate PDF
        pdf_path = f"reports/scan_{scan_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        os.makedirs('reports', exist_ok=True)
        
        pdf_generator.generate_report(scan_data, pdf_path)
        
        # Send file
        return send_file(pdf_path, as_attachment=True, 
                        download_name=f'security_scan_{scan_id}.pdf',
                        mimetype='application/pdf')
    except Exception as e:
        logger.error("pdf_generation_failed", error=str(e))
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to scanner'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    if request.sid in active_scans:
        del active_scans[request.sid]

@socketio.on('start_scan')
def handle_scan(data):
    """Handle scan request with real-time updates."""
    url = data.get('url', '')
    sid = request.sid
    
    if not url:
        emit('scan_error', {'error': 'URL is required'})
        return
    
    # Create progress callback
    progress = ProgressCallback(sid)
    active_scans[sid] = progress
    
    # Run scan in background thread
    def run_scan():
        start_time = time.time()
        try:
            # Create scanner with progress callback
            scanner = WebScanner(url, timeout=10, progress_callback=progress)
            results = asyncio.run(scanner.scan())
            report = scanner.generate_report()
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Save to database
            scan_id = db.save_scan(results, report, duration)
            
            socketio.emit('scan_complete', {
                'success': True,
                'results': results,
                'report': report,
                'scan_id': scan_id,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            }, room=sid)
        except Exception as e:
            socketio.emit('scan_error', {
                'success': False,
                'error': str(e)
            }, room=sid)
        finally:
            if sid in active_scans:
                del active_scans[sid]
    
    thread = threading.Thread(target=run_scan)
    thread.daemon = True
    thread.start()
    
    emit('scan_started', {'message': 'Scan started'})

if __name__ == '__main__':
    print("🔴 The Red Room - Real-Time Security Scanner")
    print("=" * 50)
    print("Server starting on http://127.0.0.1:5000")
    print("Features: Real-time progress, 70 vulnerability tests")
    print("=" * 50)
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
