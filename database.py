import sqlite3

def init_db():
    conn = sqlite3.connect("business.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        idea TEXT,
        budget INTEGER,
        experience TEXT,
        model TEXT,
        trend INTEGER,
        risk INTEGER,
        health INTEGER
    )
    """)

    conn.commit()
    conn.close()


def save_report(idea, budget, exp, model, trend, risk, health):
    conn = sqlite3.connect("business.db")
    c = conn.cursor()

    c.execute("""
    INSERT INTO reports (idea, budget, experience, model, trend, risk, health)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (idea, budget, exp, model, trend, risk, health))

    conn.commit()
    conn.close()


def get_reports():
    conn = sqlite3.connect("business.db")
    c = conn.cursor()

    c.execute("SELECT * FROM reports ORDER BY id DESC")
    data = c.fetchall()

    conn.close()
    return data

def delete_report(report_id):
    conn = sqlite3.connect("business.db")
    c = conn.cursor()

    c.execute("DELETE FROM reports WHERE id = ?", (report_id,))

    conn.commit()
    conn.close()