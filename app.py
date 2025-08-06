from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

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
        c.execute("SELECT * FROM reminders")
        reminders = c.fetchall()

        c.execute("SELECT title, due_date, due_time FROM reminders WHERE category='Class' AND week=?", (selected_week,))
        classes = c.fetchall()

    return render_template('index.html', reminders=reminders, classes=classes, selected_week=selected_week)

@app.route('/add', methods=['POST'])
def add():
    title = request.form['title']
    due_date = request.form['due_date']
    time_am = request.form['due_time_am']
    time_pm = request.form['due_time_pm']
    category = request.form['category']
    week = request.form.get('week', 'A')

    due_time = time_am if time_am else time_pm

    with sqlite3.connect('data.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO reminders (title, due_date, due_time, category, week) VALUES (?, ?, ?, ?, ?)",
                  (title, due_date, due_time, category, week))
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
