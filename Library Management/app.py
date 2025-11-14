#cat > app.py <<'EOF'
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import sqlite3
from datetime import datetime, timedelta
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'library.db')

app = Flask(__name__)
app.secret_key = 'replace-with-a-secure-random-key'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    if not os.path.exists(DB_PATH):
        with app.app_context():
            db = get_db()
            with open(os.path.join(BASE_DIR, 'schema.sql'), 'r') as f:
                db.executescript(f.read())
            db.commit()

from functools import wraps
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash('Access denied for your role.', 'danger')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return wrapped
    return decorator

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','').strip()
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'info')
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role') == 'admin':
        return render_template('home_admin.html')
    return render_template('home_user.html')

# -----------------------
# Maintenance (Admin only)
# -----------------------
@app.route('/maintenance')
@login_required(role='admin')
def maintenance():
    return render_template('maintenance.html')

# Add membership
@app.route('/maintenance/add_membership', methods=['GET','POST'])
@login_required(role='admin')
def add_membership():
    db = get_db()
    if request.method == 'POST':
        membership_no = request.form['membership_no'].strip()
        username = request.form['username'].strip()
        duration = int(request.form.get('duration', 6))
        user = db.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('add_membership'))
        start = datetime.now().date()
        end = start + timedelta(days=30*duration)
        db.execute('INSERT INTO memberships (membership_no, user_id, start_date, end_date, duration_months, status) VALUES (?,?,?,?,?,?)',
                   (membership_no, user['id'], start.isoformat(), end.isoformat(), duration, 'active'))
        db.commit()
        flash('Membership added', 'success')
        return redirect(url_for('maintenance'))
    return render_template('add_membership.html')

# Update membership
@app.route('/maintenance/update_membership', methods=['GET','POST'])
@login_required(role='admin')
def update_membership():
    db = get_db()
    if request.method == 'POST':
        membership_no = request.form['membership_no'].strip()
        action = request.form.get('action')
        row = db.execute('SELECT * FROM memberships WHERE membership_no=?', (membership_no,)).fetchone()
        if not row:
            flash('Membership not found', 'danger')
            return redirect(url_for('update_membership'))
        if action == 'extend':
            months = int(request.form.get('extend_months', 6))
            end = datetime.fromisoformat(row['end_date']).date() + timedelta(days=30*months)
            db.execute('UPDATE memberships SET end_date=?, duration_months=duration_months+? WHERE id=?',
                       (end.isoformat(), months, row['id']))
            db.commit()
            flash('Membership extended', 'success')
        elif action == 'cancel':
            db.execute('UPDATE memberships SET status=? WHERE id=?', ('cancelled', row['id']))
            db.commit()
            flash('Membership cancelled', 'info')
        return redirect(url_for('maintenance'))
    return render_template('update_membership.html')

# Add Book/Movie
@app.route('/maintenance/add_book', methods=['GET','POST'])
@login_required(role='admin')
def add_book():
    db = get_db()
    if request.method == 'POST':
        title = request.form['title'].strip()
        author = request.form['author'].strip()
        serial = request.form['serial_no'].strip()
        btype = request.form.get('type','book')
        if not title or not author or not serial:
            flash('All fields mandatory', 'danger')
            return redirect(url_for('add_book'))
        try:
            db.execute('INSERT INTO books (title, author, serial_no, type, available) VALUES (?,?,?,?,1)', (title, author, serial, btype))
            db.commit()
            flash('Book/Movie added', 'success')
        except sqlite3.IntegrityError:
            flash('Serial number must be unique', 'danger')
        return redirect(url_for('maintenance'))
    return render_template('add_book.html')

# Update Book/Movie
@app.route('/maintenance/update_book', methods=['GET','POST'])
@login_required(role='admin')
def update_book():
    db = get_db()
    if request.method == 'POST':
        serial = request.form['serial_no'].strip()
        title = request.form['title'].strip()
        author = request.form['author'].strip()
        btype = request.form.get('type','book')
        row = db.execute('SELECT * FROM books WHERE serial_no=?', (serial,)).fetchone()
        if not row:
            flash('Book not found', 'danger')
            return redirect(url_for('update_book'))
        if not title or not author:
            flash('All fields mandatory', 'danger')
            return redirect(url_for('update_book'))
        db.execute('UPDATE books SET title=?, author=?, type=? WHERE id=?', (title, author, btype, row['id']))
        db.commit()
        flash('Book updated', 'success')
        return redirect(url_for('maintenance'))
    return render_template('update_book.html')

# Add user
@app.route('/maintenance/add_user', methods=['GET','POST'])
@login_required(role='admin')
def add_user():
    db = get_db()
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        name = request.form['name'].strip()
        role = request.form.get('role','user')
        if not username or not password or not name:
            flash('All fields mandatory', 'danger')
            return redirect(url_for('add_user'))
        try:
            db.execute('INSERT INTO users (username, password, name, role) VALUES (?,?,?,?)', (username, password, name, role))
            db.commit()
            flash('User added', 'success')
        except sqlite3.IntegrityError:
            flash('Username already exists', 'danger')
        return redirect(url_for('maintenance'))
    return render_template('add_user.html')

# Update user
@app.route('/maintenance/update_user', methods=['GET','POST'])
@login_required(role='admin')
def update_user():
    db = get_db()
    if request.method == 'POST':
        username = request.form['username'].strip()
        name = request.form['name'].strip()
        role = request.form.get('role','user')
        row = db.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        if not row:
            flash('User not found', 'danger')
            return redirect(url_for('update_user'))
        if not name:
            flash('Name mandatory', 'danger')
            return redirect(url_for('update_user'))
        db.execute('UPDATE users SET name=?, role=? WHERE id=?', (name, role, row['id']))
        db.commit()
        flash('User updated', 'success')
        return redirect(url_for('maintenance'))
    return render_template('update_user.html')

# -----------------------
# Reports (both roles)
# -----------------------
@app.route('/reports')
@login_required()
def reports():
    db = get_db()
    books = db.execute('SELECT * FROM books').fetchall()
    memberships = db.execute('SELECT m.*, u.username FROM memberships m JOIN users u ON m.user_id=u.id').fetchall()
    active_issues = db.execute('SELECT i.*, b.title, u.username FROM issues i JOIN books b ON i.book_id=b.id JOIN users u ON i.user_id=u.id WHERE actual_return_date IS NULL').fetchall()
    overdue = []
    today = datetime.now().date().isoformat()
    for row in active_issues:
        if row['return_date'] < today:
            overdue.append(row)
    movies = [b for b in books if b['type']=='movie']
    books_only = [b for b in books if b['type']=='book']
    return render_template('reports.html', books=books_only, movies=movies, memberships=memberships, active_issues=active_issues, overdue=overdue)

# -----------------------
# Transactions (both roles)
# -----------------------
@app.route('/transactions/check', methods=['GET','POST'])
@login_required()
def check_availability():
    db = get_db()
    results = []
    if request.method == 'POST':
        title = request.form.get('title','').strip()
        author = request.form.get('author','').strip()
        q = "SELECT * FROM books WHERE 1=1"
        params = []
        if title:
            q += " AND title LIKE ?"
            params.append('%'+title+'%')
        if author:
            q += " AND author LIKE ?"
            params.append('%'+author+'%')
        results = db.execute(q, params).fetchall()
    return render_template('check_availability.html', results=results)

@app.route('/transactions/issue/<int:book_id>', methods=['GET','POST'])
@login_required()
def issue_book(book_id):
    db = get_db()
    book = db.execute('SELECT * FROM books WHERE id=?', (book_id,)).fetchone()
    if not book:
        flash('Book not found', 'danger')
        return redirect(url_for('check_availability'))
    if request.method == 'POST':
        user_id = session['user_id'] if session.get('role') == 'user' else int(request.form.get('user_id', session['user_id']))
        issue_date_str = request.form.get('issue_date')
        return_date_str = request.form.get('return_date')
        today = datetime.now().date()
        try:
            issue_date = datetime.fromisoformat(issue_date_str).date()
            return_date = datetime.fromisoformat(return_date_str).date()
        except Exception:
            flash('Invalid dates', 'danger')
            return redirect(url_for('issue_book', book_id=book_id))
        if issue_date < today:
            flash('Issue date cannot be earlier than today', 'danger')
            return redirect(url_for('issue_book', book_id=book_id))
        max_return = issue_date + timedelta(days=15)
        if return_date > max_return:
            flash('Return date cannot be greater than 15 days from issue date', 'danger')
            return redirect(url_for('issue_book', book_id=book_id))
        db.execute('INSERT INTO issues (user_id, book_id, issue_date, return_date, fine_paid) VALUES (?,?,?,?,0)',
                   (user_id, book_id, issue_date.isoformat(), return_date.isoformat()))
        db.execute('UPDATE books SET available=0 WHERE id=?', (book_id,))
        db.commit()
        flash('Book issued', 'success')
        return redirect(url_for('reports'))
    today = datetime.now().date()
    default_return = today + timedelta(days=15)
    users = db.execute('SELECT * FROM users').fetchall() if session.get('role')=='admin' else []
    return render_template('issue_book.html', book=book, default_issue=today.isoformat(), default_return=default_return.isoformat(), users=users)

@app.route('/transactions/return/<int:issue_id>', methods=['GET','POST'])
@login_required()
def return_book(issue_id):
    db = get_db()
    issue = db.execute('SELECT i.*, b.title, b.serial_no, b.id as bookid FROM issues i JOIN books b ON i.book_id=b.id WHERE i.id=?', (issue_id,)).fetchone()
    if not issue:
        flash('Issue not found', 'danger')
        return redirect(url_for('reports'))
    if request.method == 'POST':
        serial_no = request.form.get('serial_no','').strip()
        if serial_no != issue['serial_no']:
            flash('Serial number mismatch (required)', 'danger')
            return redirect(url_for('return_book', issue_id=issue_id))
        today = datetime.now().date()
        due = datetime.fromisoformat(issue['return_date']).date()
        days_late = (today - due).days
        fine = 0.0
        if days_late > 0:
            fine = days_late * 1.0
        paid_checked = request.form.get('fine_paid') == 'on'
        if fine > 0 and not paid_checked:
            flash('Pending fine must be paid before completing return', 'danger')
            return redirect(url_for('return_book', issue_id=issue_id))
        actual_return = today.isoformat()
        db.execute('UPDATE issues SET actual_return_date=?, fine_paid=?, fine_amount=? WHERE id=?', (actual_return, 1 if paid_checked else 0, fine, issue_id))
        db.execute('UPDATE books SET available=1 WHERE id=?', (issue['bookid'],))
        db.commit()
        flash('Book returned. Fine: {:.2f}'.format(fine), 'success')
        return redirect(url_for('reports'))
    due = datetime.fromisoformat(issue['return_date']).date()
    today = datetime.now().date()
    days_late = (today - due).days
    fine = days_late * 1.0 if days_late > 0 else 0.0
    return render_template('return_book.html', issue=issue, fine=fine)

@app.route('/transactions/payfine/<int:issue_id>', methods=['GET','POST'])
@login_required()
def pay_fine(issue_id):
    db = get_db()
    issue = db.execute('SELECT i.*, b.title FROM issues i JOIN books b ON i.book_id=b.id WHERE i.id=?', (issue_id,)).fetchone()
    if not issue:
        flash('Issue not found', 'danger')
        return redirect(url_for('reports'))
    due = datetime.fromisoformat(issue['return_date']).date()
    today = datetime.now().date()
    days_late = (today - due).days
    fine = days_late * 1.0 if days_late > 0 else 0.0
    if request.method == 'POST':
        paid = request.form.get('confirm') == 'on'
        if fine > 0 and not paid:
            flash('Please confirm payment to complete', 'danger')
            return redirect(url_for('pay_fine', issue_id=issue_id))
        db.execute('UPDATE issues SET fine_paid=1, fine_amount=? WHERE id=?', (fine, issue_id))
        db.commit()
        flash('Fine processed (amount: {:.2f})'.format(fine), 'success')
        return redirect(url_for('reports'))
    return render_template('pay_fine.html', issue=issue, fine=fine)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5001)