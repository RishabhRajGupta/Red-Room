"""Demo vulnerable Flask app for testing The Red Room."""

from flask import Flask, request, jsonify
import sqlite3
import time

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('demo.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY,
            username TEXT,
            balance REAL
        )
    ''')
    cursor.execute('DELETE FROM accounts')
    cursor.execute('INSERT INTO accounts VALUES (1, "alice", 1000.0)')
    cursor.execute('INSERT INTO accounts VALUES (2, "bob", 500.0)')
    conn.commit()
    conn.close()

init_db()


@app.route('/')
def home():
    return jsonify({
        "message": "Demo Vulnerable App",
        "endpoints": [
            "/api/search?q=<query>",
            "/api/transfer",
            "/api/comment"
        ]
    })


# VULNERABILITY 1: SQL Injection
@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    
    # VULNERABLE: Direct string concatenation
    conn = sqlite3.connect('demo.db')
    cursor = conn.cursor()
    sql = f"SELECT * FROM accounts WHERE username LIKE '%{query}%'"
    
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        conn.close()
        return jsonify({"results": results})
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500


# VULNERABILITY 2: Race Condition
@app.route('/api/transfer', methods=['POST'])
def transfer():
    data = request.json
    from_id = data.get('from_id')
    to_id = data.get('to_id')
    amount = data.get('amount')
    
    conn = sqlite3.connect('demo.db')
    cursor = conn.cursor()
    
    # VULNERABLE: Non-atomic balance check
    cursor.execute('SELECT balance FROM accounts WHERE id = ?', (from_id,))
    balance = cursor.fetchone()[0]
    
    if balance >= amount:
        # Race condition window!
        time.sleep(0.1)
        
        cursor.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', (amount, from_id))
        cursor.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (amount, to_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    
    conn.close()
    return jsonify({"status": "insufficient_funds"}), 400


# VULNERABILITY 3: XSS
@app.route('/api/comment', methods=['POST'])
def comment():
    data = request.json
    comment_text = data.get('comment', '')
    
    # VULNERABLE: No sanitization
    return jsonify({
        "message": f"Comment posted: {comment_text}",
        "html": f"<div>{comment_text}</div>"
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
