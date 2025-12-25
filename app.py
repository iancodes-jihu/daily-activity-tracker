import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DATABASE = "db/activities.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    with open("db/init_db.sql") as f:
        conn.executescript(f.read())
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/activity", methods=["POST"])
def add_activity():
    description = request.form["description"]
    date = request.form["date"]
    duration = request.form.get("duration")

    conn = get_db()
    conn.execute(
        "INSERT INTO activity (description, date, duration) VALUES (?, ?, ?)",
        (description, date, duration)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
