from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

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
    conn.execute(
        "INSERT INTO bewerbungen (firma, stelle, status, notizen) VALUES (?, ?, ?, ?)",
        (firma, stelle, status, notizen)
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

if __name__ == "__main__":
    app.run(debug=True)




    