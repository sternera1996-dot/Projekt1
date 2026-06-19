import sqlite3
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)
DB_FILE = "data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mereni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            u1 REAL, u2 REAL, u3 REAL,
            i1 REAL, i2 REAL, i3 REAL,
            p1 REAL, p2 REAL, p3 REAL,
            celkova_spotreba REAL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, u1, u2, u3, i1, i2, i3, p1, p2, p3, celkova_spotreba 
        FROM mereni ORDER BY id DESC LIMIT 50
    ''')
    rows = cursor.fetchall()
    conn.close()
    return render_template('index.html', data=rows)

@app.route('/api/data', methods=['POST'])
def receive_data():
    req_data = request.get_json()
    
    # Seznam všech klíčů, které očekáváme z vyčítacího skriptu
    required_fields = ['u1', 'u2', 'u3', 'i1', 'i2', 'i3', 'p1', 'p2', 'p3', 'spotreba']
    if not req_data or not all(field in req_data for field in required_fields):
        return jsonify({"status": "error", "message": "Chybějící data pro fáze"}), 400
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO mereni (timestamp, u1, u2, u3, i1, i2, i3, p1, p2, p3, celkova_spotreba)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        timestamp, 
        req_data['u1'], req_data['u2'], req_data['u3'],
        req_data['i1'], req_data['i2'], req_data['i3'],
        req_data['p1'], req_data['p2'], req_data['p3'],
        req_data['spotreba']
    ))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "message": "Třífázová data uložena"}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
