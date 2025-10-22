from flask import Flask, request, jsonify, render_template, abort
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)

# Since frontend and backend are served on same port, CORS can be relaxed or removed
# But to be safe, allow all origins or remove CORS if not needed
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.after_request
def add_cors_headers(response):
    # Allow all origins or restrict as needed
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# MySQL configurations - update these with your MySQL credentials
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mySqlroot@1011'
app.config['MYSQL_DB'] = 'user_auth_db'

mysql = MySQL(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Frontend routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/home.html')
def home_html():
    return render_template('home.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/adminlogin')
def adminlogin_page():
    return render_template('adminlogin.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/checkreport')
def checkreport_page():
    return render_template('checkreport.html')

@app.route('/report')
def report_page():
    return render_template('report.html')

# API routes
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Please provide username, email, and password'}), 400

    cur = mysql.connection.cursor()
    # Check if user already exists
    cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
    existing_user = cur.fetchone()
    if existing_user:
        return jsonify({'error': 'User with this username or email already exists'}), 409

    hashed_password = generate_password_hash(password)
    cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_password))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Please provide username and password'}), 400

    cur = mysql.connection.cursor()
    cur.execute("SELECT password FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()

    if user and check_password_hash(user[0], password):
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/users', methods=['GET'])
def get_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT username, email FROM users")
    users = cur.fetchall()
    cur.close()
    users_list = [{'username': u[0], 'email': u[1]} for u in users]
    return jsonify(users_list)

@app.route('/report', methods=['POST'])
def submit_report():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400
    image = request.files['image']
    issue_type = request.form.get('issue_type')
    description = request.form.get('description')

    if not issue_type or not description:
        return jsonify({'error': 'Please provide issue type and description'}), 400

    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp_str}_{filename}"
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    else:
        image_path = None

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO reports (issue_type, description, image_path, timestamp)
        VALUES (%s, %s, %s, %s)
    """, (issue_type, description, image_path, datetime.now()))
    mysql.connection.commit()
    report_id = cur.lastrowid
    cur.close()

    return jsonify({'message': 'Report submitted successfully', 'id': report_id}), 201

@app.route('/workers', methods=['GET'])
def get_workers():
    location = request.args.get('location')
    issue_type = request.args.get('issue_type')
    cur = mysql.connection.cursor()
    if location and issue_type:
        query = "SELECT id, name FROM workers WHERE LOWER(location) = %s"
        cur.execute(query, (location.lower(),))
    elif location:
        query = "SELECT id, name FROM workers WHERE LOWER(location) = %s"
        cur.execute(query, (location.lower(),))
    elif issue_type:
        query = "SELECT id, name FROM workers"
        cur.execute(query)
    else:
        cur.execute("SELECT id, name FROM workers")
    workers = cur.fetchall()
    cur.close()
    workers_list = [{'id': w[0], 'name': w[1]} for w in workers]
    return jsonify(workers_list)

@app.route('/admin/reports', methods=['GET'])
def get_admin_reports():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, issue_type, description, image_path, timestamp, status FROM reports")
    reports = cur.fetchall()
    cur.close()
    reports_list = []
    for r in reports:
        reports_list.append({
            'id': r[0],
            'issue_type': r[1],
            'description': r[2],
            'image_path': r[3],
            'timestamp': r[4].isoformat() if r[4] else None,
            'status': r[5] if r[5] else 'pending'
        })
    return jsonify(reports_list)

@app.route('/admin/reports/<int:report_id>/approve', methods=['POST'])
def approve_report(report_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE reports SET status = 'approved' WHERE id = %s", (report_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Report approved successfully'})

@app.route('/admin/reports/<int:report_id>/decline', methods=['POST'])
def decline_report(report_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE reports SET status = 'declined' WHERE id = %s", (report_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Report declined successfully'})

from flask import abort

@app.route('/report/<int:report_id>', methods=['GET'])
def get_report(report_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, issue_type, description, image_path, timestamp, status FROM reports WHERE id = %s", (report_id,))
    report = cur.fetchone()
    cur.close()
    if report:
        report_data = {
            'id': report[0],
            'issue_type': report[1],
            'description': report[2],
            'image_path': report[3],
            'timestamp': report[4].isoformat() if report[4] else None,
            'status': report[5] if report[5] else 'pending'
        }
        return jsonify(report_data)
    else:
        abort(404, description="Report not found")

@app.route('/user/<username>/has_reports', methods=['GET'])
def user_has_reports(username):
    cur = mysql.connection.cursor()
    # Assuming reports table has a 'username' column linking reports to users
    cur.execute("SELECT COUNT(*) FROM reports WHERE username = %s", (username,))
    count = cur.fetchone()[0]
    cur.close()
    return jsonify({'has_reports': count > 0})

@app.route('/test', methods=['GET'])
def test_route():
    return jsonify({'message': 'Test route is working'})

@app.route('/admin/reports/<int:report_id>/assign_worker', methods=['POST'])
def assign_worker(report_id):
    data = request.get_json()
    worker_id = data.get('worker_id')
    if not worker_id:
        return jsonify({'error': 'worker_id is required'}), 400

    cur = mysql.connection.cursor()
    # Assuming reports table has a column 'assigned_worker_id' to store the assigned worker
    cur.execute("UPDATE reports SET assigned_worker_id = %s WHERE id = %s", (worker_id, report_id))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Worker assigned successfully'})

if __name__ == '__main__':
    app.run(debug=True)
