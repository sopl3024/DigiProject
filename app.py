from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Week A or B
def get_week_ab(date_str):
    """Given a date string YYYY-MM-DD, return 'A' or 'B'."""
    date = datetime.strptime(date_str, "%Y-%m-%d")
    year_start = datetime(date.year, 1, 1)

    # Find the first Monday of the year
    first_monday = year_start + timedelta(days=(7 - year_start.weekday()) % 7)

    # How many full weeks have passed since that first Monday
    week_number = ((date - first_monday).days // 7)

    return 'A' if week_number % 2 == 0 else 'B'

# Format for rendering dates in timetable
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%H:%M'):
    try:
        return datetime.strptime(value, '%Y-%m-%d').strftime(format)
    except:
        return value

# Initialize database
def init_db():
    with sqlite3.connect('data.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            due_date TEXT,
            due_time TEXT,
            category TEXT,
            completed INTEGER DEFAULT 0,
            week TEXT DEFAULT 'A'
        )''')
        conn.commit()

@app.route('/')
def index():
    selected_week = request.args.get('week', 'A')
    with sqlite3.connect('data.db') as conn:
        c = conn.cursor()

        # Sort all reminders by combined datetime
        c.execute("""
            SELECT * FROM reminders
            ORDER BY datetime(due_date || ' ' || due_time) ASC
        """)
        reminders = c.fetchall()

        # Sort only "Class" category reminders for timetable by combined datetime
        c.execute("""
            SELECT title, due_date, due_time
            FROM reminders
            WHERE category='Class' AND week=?
            ORDER BY datetime(due_date || ' ' || due_time) ASC
        """, (selected_week,))
        classes = c.fetchall()

    return render_template('index.html', reminders=reminders, classes=classes, selected_week=selected_week)

@app.route('/add', methods=['POST'])
def add_reminder():
    title = request.form['title']
    due_date = request.form['due_date']
    due_time = request.form.get('due_time_am') or request.form.get('due_time_pm')
    category = request.form['category']
    completed = 0

    # Automatically assign week based on date for "Class" category
    week = get_week_ab(due_date) if category == 'Class' else ''

    with sqlite3.connect('data.db') as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO reminders (title, due_date, due_time, category, completed, week)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, due_date, due_time, category, completed, week))
        conn.commit()
    return redirect('/')

@app.route('/complete/<int:reminder_id>')
def complete(reminder_id):
    with sqlite3.connect('data.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE reminders SET completed = 1 WHERE id = ?", (reminder_id,))
        conn.commit()
    return redirect('/')

@app.route('/uncomplete/<int:reminder_id>')
def uncomplete(reminder_id):
    with sqlite3.connect('data.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE reminders SET completed = 0 WHERE id = ?", (reminder_id,))
        conn.commit()
    return redirect('/')

@app.route('/delete/<int:reminder_id>')
def delete(reminder_id):
    with sqlite3.connect('data.db') as conn:
        c = conn.cursor()
        c.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        conn.commit()
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
