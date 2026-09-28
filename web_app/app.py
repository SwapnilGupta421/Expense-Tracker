import csv
import io
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

from flask import Flask, make_response, render_template, request, redirect, session, g, abort
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-dev-key')

DATABASE = 'expenses.db'
ALLOWED_CATEGORIES = ['Travel', 'Food', 'Shopping', 'Health', 'Other']


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    with open('schema.sql') as f:
        db.executescript(f.read())
    db.close()


init_db()


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif password != confirm:
            error = 'Passwords do not match.'
        elif len(password) < 4:
            error = 'Password must be at least 4 characters.'
        else:
            try:
                db = get_db()
                existing = db.execute(
                    'SELECT id FROM users WHERE email = ?', (email,)
                ).fetchone()
                if existing:
                    error = 'Email already registered.'
                else:
                    pw_hash = generate_password_hash(password)
                    db.execute(
                        'INSERT INTO users (email, password_hash) VALUES (?, ?)',
                        (email, pw_hash)
                    )
                    db.commit()
                    return redirect('/login')
            except Exception:
                error = 'An unexpected error occurred. Please try again.'

    return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        else:
            try:
                db = get_db()
                user = db.execute(
                    'SELECT * FROM users WHERE email = ?', (email,)
                ).fetchone()
                if not user or not check_password_hash(user['password_hash'], password):
                    error = 'Invalid email or password.'
                else:
                    session['user_id'] = user['id']
                    return redirect('/')
            except Exception:
                error = 'An unexpected error occurred. Please try again.'

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    db = get_db()
    today = datetime.now()
    current_month = today.strftime('%Y-%m')

    try:
        expenses = db.execute(
            'SELECT * FROM expenses WHERE user_id = ? AND strftime("%Y-%m", date) = ? ORDER BY date DESC',
            (user_id, current_month)
        ).fetchall()

        total = sum(row['amount'] for row in expenses)

        category_totals = {}
        for row in expenses:
            cat = row['category']
            category_totals[cat] = category_totals.get(cat, 0) + row['amount']

        year_rows = db.execute(
            'SELECT DISTINCT strftime("%Y", date) as y FROM expenses WHERE user_id = ? ORDER BY y DESC',
            (user_id,)
        ).fetchall()
        available_years = [r['y'] for r in year_rows]

        top_category = max(category_totals, key=category_totals.get) if category_totals else None
        top_amount = category_totals[top_category] if top_category else 0

        monthly_trends = db.execute(
            'SELECT strftime("%Y-%m", date) as month, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY month ORDER BY month ASC',
            (user_id,)
        ).fetchall()
    except Exception:
        return render_template('dashboard.html', error='Could not load expenses.',
                               expenses=[], total=0, category_totals={},
                               current_month=current_month, available_years=[],
                               search_q='', search_category='', search_month='', show_all=False,
                               categories=ALLOWED_CATEGORIES, top_category=None, top_amount=0,
                               monthly_trends=[])

    return render_template('dashboard.html', expenses=expenses, total=total,
                           category_totals=category_totals,
                           current_month=current_month, available_years=available_years,
                           search_q='', search_category='', search_month='', show_all=False,
                           categories=ALLOWED_CATEGORIES, top_category=top_category,
                           top_amount=top_amount, monthly_trends=monthly_trends)


@app.route('/all')
def all_expenses():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    db = get_db()

    try:
        expenses = db.execute(
            'SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC',
            (user_id,)
        ).fetchall()

        total = sum(row['amount'] for row in expenses)

        category_totals = {}
        for row in expenses:
            cat = row['category']
            category_totals[cat] = category_totals.get(cat, 0) + row['amount']

        year_rows = db.execute(
            'SELECT DISTINCT strftime("%Y", date) as y FROM expenses WHERE user_id = ? ORDER BY y DESC',
            (user_id,)
        ).fetchall()
        available_years = [r['y'] for r in year_rows]

        top_category = max(category_totals, key=category_totals.get) if category_totals else None
        top_amount = category_totals[top_category] if top_category else 0

        monthly_trends = db.execute(
            'SELECT strftime("%Y-%m", date) as month, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY month ORDER BY month ASC',
            (user_id,)
        ).fetchall()
    except Exception:
        return render_template('dashboard.html', error='Could not load expenses.',
                               expenses=[], total=0, category_totals={},
                               current_month='', show_all=True, available_years=[],
                               search_q='', search_category='', search_month='',
                               categories=ALLOWED_CATEGORIES, top_category=None, top_amount=0,
                               monthly_trends=[])

    return render_template('dashboard.html', expenses=expenses, total=total,
                           category_totals=category_totals,
                           current_month='', show_all=True, available_years=available_years,
                           search_q='', search_category='', search_month='',
                           categories=ALLOWED_CATEGORIES, top_category=top_category,
                           top_amount=top_amount, monthly_trends=monthly_trends)


@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect('/login')

    error = None
    form_data = {}

    if request.method == 'POST':
        amount = request.form.get('amount', '').strip()
        category = request.form.get('category', '').strip()
        date = request.form.get('date', '').strip()
        note = request.form.get('note', '').strip()

        form_data = {
            'amount': amount,
            'category': category,
            'date': date,
            'note': note,
        }

        if not amount:
            error = 'Amount is required.'
        else:
            try:
                amount_val = float(amount)
                if amount_val <= 0:
                    error = 'Amount must be a positive number.'
            except ValueError:
                error = 'Amount must be a valid number.'

        if not error:
            if category not in ALLOWED_CATEGORIES:
                error = 'Please select a valid category.'

        if not error:
            if not date:
                error = 'Date is required.'

        if not error:
            try:
                db = get_db()
                db.execute(
                    'INSERT INTO expenses (user_id, amount, category, date, note) VALUES (?, ?, ?, ?, ?)',
                    (session['user_id'], amount_val, category, date, note)
                )
                db.commit()
                return redirect('/')
            except Exception:
                error = 'An unexpected error occurred. Please try again.'

    return render_template('add_expense.html', error=error, form_data=form_data,
                           categories=ALLOWED_CATEGORIES)


@app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    try:
        expense = db.execute(
            'SELECT * FROM expenses WHERE id = ?', (expense_id,)
        ).fetchone()
    except Exception:
        abort(500)

    if not expense:
        abort(404)

    if expense['user_id'] != session['user_id']:
        abort(403)

    error = None
    form_data = {
        'amount': expense['amount'],
        'category': expense['category'],
        'date': expense['date'],
        'note': expense['note'] or '',
    }

    if request.method == 'POST':
        amount = request.form.get('amount', '').strip()
        category = request.form.get('category', '').strip()
        date = request.form.get('date', '').strip()
        note = request.form.get('note', '').strip()

        form_data = {
            'amount': amount,
            'category': category,
            'date': date,
            'note': note,
        }

        if not amount:
            error = 'Amount is required.'
        else:
            try:
                amount_val = float(amount)
                if amount_val <= 0:
                    error = 'Amount must be a positive number.'
            except ValueError:
                error = 'Amount must be a valid number.'

        if not error:
            if category not in ALLOWED_CATEGORIES:
                error = 'Please select a valid category.'

        if not error:
            if not date:
                error = 'Date is required.'

        if not error:
            try:
                db.execute(
                    'UPDATE expenses SET amount=?, category=?, date=?, note=? WHERE id=?',
                    (amount_val, category, date, note, expense_id)
                )
                db.commit()
                return redirect('/')
            except Exception:
                error = 'An unexpected error occurred. Please try again.'

    return render_template('add_expense.html', error=error, form_data=form_data,
                           categories=ALLOWED_CATEGORIES, edit_mode=True, expense_id=expense_id)




@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    try:
        expense = db.execute(
            'SELECT * FROM expenses WHERE id = ?', (expense_id,)
        ).fetchone()
    except Exception:
        abort(500)

    if not expense:
        abort(404)

    if expense['user_id'] != session['user_id']:
        abort(403)

    try:
        db.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        db.commit()
    except Exception:
        abort(500)

    return redirect('/')


@app.route('/search')
def search():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    db = get_db()

    search_q = request.args.get('q', '').strip()
    search_category = request.args.get('category', '').strip()
    search_month = request.args.get('month', '').strip()
    search_year = request.args.get('year', '').strip()

    query = 'SELECT * FROM expenses WHERE user_id = ?'
    params = [user_id]

    if search_q:
        query += ' AND note LIKE ?'
        params.append(f'%{search_q}%')

    if search_category and search_category in ALLOWED_CATEGORIES:
        query += ' AND category = ?'
        params.append(search_category)

    if search_month:
        query += ' AND strftime("%Y-%m", date) = ?'
        params.append(search_month)

    if search_year:
        query += ' AND strftime("%Y", date) = ?'
        params.append(search_year)

    query += ' ORDER BY date DESC'

    try:
        expenses = db.execute(query, params).fetchall()
        total = sum(row['amount'] for row in expenses)

        category_totals = {}
        for row in expenses:
            cat = row['category']
            category_totals[cat] = category_totals.get(cat, 0) + row['amount']

        year_rows = db.execute(
            'SELECT DISTINCT strftime("%Y", date) as y FROM expenses WHERE user_id = ? ORDER BY y DESC',
            (user_id,)
        ).fetchall()
        available_years = [r['y'] for r in year_rows]

        top_category = max(category_totals, key=category_totals.get) if category_totals else None
        top_amount = category_totals[top_category] if top_category else 0

        monthly_trends = db.execute(
            'SELECT strftime("%Y-%m", date) as month, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY month ORDER BY month ASC',
            (user_id,)
        ).fetchall()
    except Exception:
        return render_template('dashboard.html', error='Search failed. Please try again.',
                               expenses=[], total=0, category_totals={},
                               current_month=search_month or datetime.now().strftime('%Y-%m'),
                               available_years=[],
                               search_q=search_q, search_category=search_category,
                               search_month=search_month, search_year=search_year,
                               show_all=False, categories=ALLOWED_CATEGORIES,
                               top_category=None, top_amount=0, monthly_trends=[])

    current_month = search_month if search_month else datetime.now().strftime('%Y-%m')

    return render_template('dashboard.html', expenses=expenses, total=total,
                           category_totals=category_totals,
                           current_month=current_month, available_years=available_years,
                           search_q=search_q, search_category=search_category,
                           search_month=search_month, search_year=search_year,
                           show_all=False, categories=ALLOWED_CATEGORIES,
                           top_category=top_category, top_amount=top_amount,
                           monthly_trends=monthly_trends)


@app.route('/export/csv')
def export_csv():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    db = get_db()

    try:
        expenses = db.execute(
            'SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC',
            (user_id,)
        ).fetchall()
    except Exception:
        abort(500)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Category', 'Amount', 'Note'])
    for row in expenses:
        writer.writerow([row['date'], row['category'], f'{row["amount"]:.2f}', row['note'] or ''])

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=expenses.csv'
    return response


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Forbidden'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error'), 500


if __name__ == '__main__':
    app.run(debug=True)