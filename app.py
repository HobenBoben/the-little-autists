from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = "SUPER_SECRET_KEY"

ADMIN_LOGIN = "admin"
ADMIN_PASSWORD = "12345"

# Настройки загрузки файлов
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'mp4', 'webm', 'avi', 'mov', 'mkv', 'zip', 'mcworld'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def db():
    return sqlite3.connect("database.db")

# Фильтр для форматирования даты
@app.template_filter('datetime')
def format_datetime(value, format='%d.%m.%Y %H:%M'):
    if value is None:
        return ''
    try:
        dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return dt.strftime(format)
    except:
        return value

@app.route("/")
def index():
    con = db()
    news = con.execute("SELECT * FROM news ORDER BY id DESC").fetchall()
    return render_template("index.html", news=news)

@app.route("/team")
def team():
    con = db()
    players = con.execute("SELECT * FROM players").fetchall()
    return render_template("team.html", players=players)

@app.route("/player/<int:id>")
def player(id):
    con = db()
    player = con.execute("SELECT * FROM players WHERE id=?", (id,)).fetchone()
    return render_template("player.html", player=player)

@app.route("/matches")
def matches():
    con = db()
    matches = con.execute("SELECT * FROM matches").fetchall()
    return render_template("matches.html", matches=matches)

@app.route("/replays")
def replays():
    con = db()
    replays = con.execute("SELECT * FROM replays").fetchall()
    return render_template("replays.html", replays=replays)

# --- LOGIN ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["login"] == ADMIN_LOGIN and request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
    return render_template("login.html")

@app.route("/admin", methods=["GET","POST"])
def admin():
    if not session.get("admin"):
        return redirect("/login")

    con = db()

    if request.method == "POST":
        if "news" in request.form:
            con.execute("INSERT INTO news(title, text) VALUES(?,?)",
                        (request.form["title"], request.form["text"]))
            con.commit()

        if "player" in request.form:
            con.execute("INSERT INTO players(name, role, stats) VALUES(?,?,?)",
                        (request.form["name"], request.form["role"], request.form["stats"]))
            con.commit()

        if "match" in request.form:
            con.execute("INSERT INTO matches(opponent, score, date) VALUES(?,?,?)",
                        (request.form["opponent"], request.form["score"], request.form["date"]))
            con.commit()

        if "replay" in request.form:
            title = request.form["title"]
            file = request.files.get("replay_file")
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                con.execute("INSERT INTO replays(title, filename) VALUES(?,?)", (title, filename))
                con.commit()
            # Можно добавить сообщение об ошибке, но для простоты опустим

    players = con.execute("SELECT * FROM players").fetchall()
    return render_template("admin.html", players=players)

@app.route("/edit_player/<int:id>", methods=["GET", "POST"])
def edit_player(id):
    if not session.get("admin"):
        return redirect("/login")

    con = db()
    if request.method == "POST":
        name = request.form["name"]
        role = request.form["role"]
        stats = request.form["stats"]
        con.execute("UPDATE players SET name=?, role=?, stats=? WHERE id=?", (name, role, stats, id))
        con.commit()
        return redirect("/admin")
    else:
        player = con.execute("SELECT * FROM players WHERE id=?", (id,)).fetchone()
        if not player:
            return "Игрок не найден", 404
        return render_template("edit_player.html", player=player)
@app.route("/news")
def news():
    con = db()
    news = con.execute("SELECT * FROM news ORDER BY id DESC").fetchall()
    return render_template("news.html", news=news)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

