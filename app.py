
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Initialize the database
def init_db():
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_date TEXT NOT NULL,
            category TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Home page
@app.route('/')
def index():
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute("SELECT * FROM reminders")
    reminders = c.fetchall()
    conn.close()
    return render_template('index.html', reminders=reminders)

# Add new reminder
@app.route('/add', methods=['POST'])
def add():
    title = request.form['title']
    due_date = request.form['due_date']
    category = request.form['category']
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute("INSERT INTO reminders (title, due_date, category) VALUES (?, ?, ?)",
              (title, due_date, category))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Mark as complete
@app.route('/complete/<int:reminder_id>')
def complete(reminder_id):
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute("UPDATE reminders SET completed = 1 WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Delete reminder
@app.route('/delete/<int:reminder_id>')
def delete(reminder_id):
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Start the app
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
