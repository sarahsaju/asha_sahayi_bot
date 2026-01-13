import sqlite3

DB_NAME = "asha_visits.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id TEXT,
            visit_date TEXT,
            patient_label TEXT,
            age_group TEXT,
            complaint TEXT,
            danger_signs TEXT,
            referral TEXT,
            notes TEXT
        )
    """)

    conn.commit()
    conn.close()

def save_visit(worker_id, visit_date, patient_label, age_group,
               complaint, danger_signs, referral, notes):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO visits
        (worker_id, visit_date, patient_label, age_group,
         complaint, danger_signs, referral, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        worker_id, visit_date, patient_label, age_group,
        complaint, danger_signs, referral, notes
    ))

    conn.commit()
    conn.close()

def get_all_visits():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM visits")
    rows = cursor.fetchall()

    conn.close()
    return rows
