import sqlite3 

def connect_db():
    db = sqlite3.connect ('database.db')
    return db

def init_db():
    connection = connect_db()
    per = connection.cursor()
    per.execute("CREATE TABLE IF NOT EXISTS projects(name TEXT,repo_url TEXT, command TEXT, port INTEGER, status TEXT, pid INTEGER)")
    connection.commit()
    connection.close()
    
def add_project_db(name, repo_url, command, port    ):
    connection = connect_db()
    per = connection.cursor()
    per.execute("INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?)",
                (name, repo_url, command, port, "stopped", None))
    connection.commit()
    connection.close()