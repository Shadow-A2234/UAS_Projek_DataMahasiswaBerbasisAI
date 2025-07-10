from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import sqlite3
import requests
import json
import io
import subprocess
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "rahasia123"

# ------------------ OpenRouter ------------------ #
OPENROUTER_API_KEY = "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"
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:5000",
    "X-Title": "Chatbot OOP LinkedList"
}
MODEL = "mistralai/mistral-7b-instruct"

# ------------------ Struktur Data ------------------ #
class ChatNode:
    def __init__(self, role, message):
        self.role = role
        self.message = message
        self.next = None

class ChatHistory:
    def __init__(self):
        self.head = None

    def add_message(self, role, message):
        new_node = ChatNode(role, message)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def to_list(self):
        messages = []
        current = self.head
        while current:
            messages.append({"role": current.role, "content": current.message})
            current = current.next
        return messages

# ------------------ Enkapsulasi ------------------ #
class Mahasiswa:
    def __init__(self, nama, nim, ipk=None):
        self.__nama = nama
        self.__nim = nim
        self.__ipk = ipk

    def get_nama(self):
        return self.__nama

    def get_nim(self):
        return self.__nim

    def get_ipk(self):
        return self.__ipk

    def set_ipk(self, ipk):
        self.__ipk = ipk

# ------------------ DB Init ------------------ #
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS mahasiswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            nim TEXT NOT NULL UNIQUE,
            ipk REAL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS riwayat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nim TEXT NOT NULL,
            messages TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("SELECT * FROM admin WHERE username=?", ("admin",))
    if not c.fetchone():
        c.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ("admin", "admin123"))
    conn.commit()
    conn.close()

init_db()

# ------------------ Login ------------------ #
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nama = request.form["nama"]
        nim = request.form["nim"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM admin WHERE username=? AND password=?", (nama, nim))
        admin_result = c.fetchone()

        if admin_result:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))

        c.execute("SELECT * FROM mahasiswa WHERE nama=? AND nim=?", (nama, nim))
        result = c.fetchone()
        conn.close()

        if result:
            session["user"] = {"nama": nama, "nim": nim}

            # ✅ Jalankan verifikasi
            try:
                verifikasi_path = os.path.join(os.path.dirname(__file__), "verifikasi.py")
                subprocess.run(["python", verifikasi_path], check=True)
            except Exception as e:
                print("❌ Gagal jalankan verifikasi:", e)

            return redirect(url_for("chat_page"))
        else:
            return render_template("login.html", error="Nama atau NIM salah.")
    return render_template("login.html")

# ------------------ Chat Page ------------------ #
@app.route("/chat_page")
def chat_page():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", user=session["user"])

@app.route("/chat", methods=["POST"])
def chat():
    if "user" not in session:
        return jsonify({"reply": "Silakan login terlebih dahulu."})

    user_input = request.json.get("message")
    user_nama = session["user"]["nama"]
    user_nim = session["user"]["nim"]

    history = ChatHistory()
    history.add_message("user", f"Halo saya {user_nama}. {user_input}")

    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": "Kamu adalah asisten AI kampus."}] + history.to_list()
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=HEADERS, json=payload)
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
        history.add_message("assistant", reply)

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO riwayat (nim, messages) VALUES (?, ?)",
                  (user_nim, json.dumps(history.to_list())))
        conn.commit()
        conn.close()
    except Exception as e:
        reply = f"⚠️ Gagal: {e}"

    return jsonify({"reply": reply})

# ------------------ Riwayat Mahasiswa ------------------ #
@app.route("/riwayat")
def riwayat():
    if "user" not in session:
        return redirect(url_for("login"))

    nim = session["user"]["nim"]
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT messages, timestamp FROM riwayat WHERE nim=? ORDER BY timestamp DESC", (nim,))
    rows = c.fetchall()
    conn.close()

    riwayat_data = []
    for msg_json, timestamp in rows:
        try:
            msg_list = json.loads(msg_json)
            riwayat_data.append((msg_list, timestamp))
        except:
            continue

    return render_template("riwayat.html", riwayat=riwayat_data, user=session["user"])

# ------------------ Admin Riwayat ------------------ #
@app.route("/riwayat_admin")
def riwayat_admin():
    if "admin" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT nim, messages, timestamp FROM riwayat ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()

    all_data = []
    for nim, msg_json, timestamp in rows:
        try:
            messages = json.loads(msg_json)
            all_data.append({"nim": nim, "messages": messages, "timestamp": timestamp})
        except:
            continue

    return render_template("admin_riwayat.html", riwayat=all_data)

@app.route("/download_riwayat_json")
def download_riwayat_json():
    if "admin" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT nim, messages, timestamp FROM riwayat")
    rows = c.fetchall()
    conn.close()

    result = []
    for nim, messages, timestamp in rows:
        result.append({"nim": nim, "messages": json.loads(messages), "timestamp": timestamp})

    buffer = io.BytesIO()
    buffer.write(json.dumps(result, indent=2).encode('utf-8'))
    buffer.seek(0)

    filename = f"riwayat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/json')

# ------------------ Admin Dashboard ------------------ #
@app.route("/admin_dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        nama = request.form["nama"]
        nim = request.form["nim"]
        ipk = request.form.get("ipk")
        c.execute("INSERT OR IGNORE INTO mahasiswa (nama, nim, ipk) VALUES (?, ?, ?)", (nama, nim, ipk))
        conn.commit()

    c.execute("SELECT id, nama, nim, ipk FROM mahasiswa")
    data = c.fetchall()
    conn.close()
    return render_template("admin_dashboard.html", mahasiswa=data)

@app.route("/update_mahasiswa/<int:id>", methods=["POST"])
def update_mahasiswa(id):
    if "admin" not in session:
        return redirect(url_for("login"))

    ipk = request.form["ipk"]
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("UPDATE mahasiswa SET ipk=? WHERE id=?", (ipk, id))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_dashboard"))

@app.route("/hapus_mahasiswa/<int:id>", methods=["POST"])
def hapus_mahasiswa(id):
    if "admin" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM mahasiswa WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_dashboard"))

# ------------------ Logout ------------------ #
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ------------------ Run ------------------ #
if __name__ == "__main__":
    app.run(debug=True)
