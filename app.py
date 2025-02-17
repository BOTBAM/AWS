from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os



app = Flask(__name__)
app.secret_key = "supersecretkey"
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"txt"}



if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)



# Initialize database
def init_db():
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL)''')
        conn.commit()
init_db()



# ---------- LOGIN PAGE (DEFAULT PAGE) ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
            user = c.fetchone()

        if user:
            session["username"] = user[1]  # Store username in session
            return redirect(url_for("profile"))
        else:
            flash("Wrong email and/or password. Please try again.", "error")

    return render_template("login.html")



# ---------- REGISTRATION PAGE ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]
        address = request.form["address"]

        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (username, password, firstname, lastname, email, address) VALUES (?, ?, ?, ?, ?, ?)",
                    (username, password, firstname, lastname, email, address))
                conn.commit()
                return redirect(url_for("login"))
            
            except sqlite3.IntegrityError:
                flash("Email alraedy registered. Try logging in.", "error")

    return render_template("register.html")



# ---------- USED TO LIMIT UPLOAD TYPES FOR USERS ----------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS



# ---------- PROFILE PAGE (AFTER LOGIN) ----------
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    word_count = None
    uploaded_filename = None

    if request.method == "POST" and "file" in request.files:
        file = request.files["file"]
        if file.filename == "":
            flash("No file selected.", "error")
        elif not allowed_file(file.filename):
            flash("Invalid file type. Only .txt files are allowed.", "error")
        else:
            uploaded_filename = file.filename
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], uploaded_filename)
            file.save(filepath)

            with open(filepath, "r") as f:
                content = f.read()
                word_count = len(content.split())

    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()

    return render_template("profile.html", user=user, word_count=word_count, uploaded_filename=uploaded_filename)




# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))




if __name__ == "__main__":
    app.run(debug=True)