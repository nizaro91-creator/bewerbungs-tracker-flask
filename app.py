from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import send_file
from datetime import datetime

import io

from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("bewerbungen.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bewerbungen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firma TEXT,
            stelle TEXT,
            status TEXT,
            notizen TEXT,
            datum TEXT
        )
    """)
    conn.close()

def get_db_connection():
    conn = sqlite3.connect("bewerbungen.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    conn = get_db_connection()
    bewerbungen = conn.execute("SELECT * FROM bewerbungen").fetchall()
    conn.close()
    return render_template("index.html", bewerbungen=bewerbungen)

@app.route("/add", methods=["POST"])
def add():
    firma = request.form["firma"]
    stelle = request.form["stelle"]
    status = request.form["status"]
    notizen = request.form["notizen"]

    conn = get_db_connection()
    now = datetime.now()
    datum = now.strftime("%d.%m.%Y")

    conn.execute(
    "INSERT INTO bewerbungen (firma, stelle, status, notizen, datum) VALUES (?, ?, ?, ?, ?)",
    (firma, stelle, status, notizen, datum)
)
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM bewerbungen WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db_connection()

    if request.method == "POST":
        firma = request.form["firma"]
        stelle = request.form["stelle"]
        status = request.form["status"]
        notizen = request.form["notizen"]

        conn.execute("""
            UPDATE bewerbungen
            SET firma = ?, stelle = ?, status = ?, notizen = ?
            WHERE id = ?
        """, (firma, stelle, status, notizen, id))

        conn.commit()
        conn.close()
        return redirect("/")

    bewerbung = conn.execute("SELECT * FROM bewerbungen WHERE id = ?", (id,)).fetchone()
    conn.close()

    return render_template("edit.html", bewerbung=bewerbung)
@app.route("/download")

def download_pdf():
    conn = get_db_connection()
    bewerbungen = conn.execute("SELECT * FROM bewerbungen").fetchall()
    conn.close()

    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    import io

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()

    elements = []

    # 🟢 TITLE
    title = Paragraph("<b>Bewerbungs Tracker</b>", styles["Title"])
    elements.append(title)
    # 📅 DATE
    now = datetime.now()
    date_str = now.strftime("%d.%m.%Y - %H:%M")

    date_paragraph = Paragraph(f"Erstellt am: {date_str}", styles["Normal"])
    elements.append(date_paragraph)

    # 🟢 SPACE
    elements.append(Paragraph("<br/>", styles["Normal"]))

    # 🟢 TABLE DATA
    data = [["Firma", "Stelle", "Status", "Notizen"]]

    for b in bewerbungen:
        data.append([
            b["firma"],
            b["stelle"],
            b["status"],
            b["notizen"]
        ])

    # 🟢 CREATE TABLE
    table = Table(data)

    # 🟢 STYLE
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),

        ("ALIGN", (0,0), (-1,-1), "CENTER"),

        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 10),

        ("BACKGROUND", (0,1), (-1,-1), colors.beige),

        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="bewerbungen.pdf", mimetype="application/pdf")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)


    
