import sqlite3

con = sqlite3.connect("database.db")

con.execute("""
    CREATE TABLE news (
        id INTEGER PRIMARY KEY,
        title TEXT,
        text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
con.execute("CREATE TABLE players(id INTEGER PRIMARY KEY, name TEXT, role TEXT, stats TEXT)")
con.execute("CREATE TABLE matches(id INTEGER PRIMARY KEY, opponent TEXT, score TEXT, date TEXT)")
con.execute("""
    CREATE TABLE replays(
        id INTEGER PRIMARY KEY,
        title TEXT,
        filename TEXT   -- имя файла в папке static/uploads
    )
""")

con.commit()