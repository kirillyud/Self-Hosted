import sqlite3 

def connect_db():
    db = sqlite3.connect ('database.db')
    return db

def init_db():
    connection = connect_db()
    per = connection.cursor()
    per.execute("CREATE TABLE IF NOT EXISTS projects(name TEXT UNIQUE,repo_url TEXT, command TEXT, port INTEGER, status TEXT, pid INTEGER)")
    connection.commit()
    connection.close()
    
def add_project_db(name, repo_url, command, port):
    connection = connect_db()
    per = connection.cursor()
    try:
        per.execute("INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?)",
                (name, repo_url, command, port, "stopped", None))
        connection.commit()
        connection.close()
        return {'success': True}
    except sqlite3.Error as er:
        connection.close()
        return {'success': False, 'error': er}

def get_projects_db():
    connection = connect_db()
    per = connection.cursor()
    per.execute("SELECT * FROM projects")
    datas = per.fetchall()
    connection.close()
    list_of_projects = []
    for data in datas:
        list_of_projects.append({'name': data[0],
            'repo_url': data[1],
            'command': data[2],
            'port': data[3],
            'status': data[4],
            'pid': data[5]})
    return list_of_projects

def get_project_db(name):
    connection = connect_db()
    per = connection.cursor()
    per.execute("SELECT * FROM projects WHERE name = ?", (name, ))
    datas = per.fetchone()
    connection.close()
    if not datas:
        return None
    return {'name': datas[0],
            'repo_url': datas[1],
            'command': datas[2],
            'port': datas[3],
            'status': datas[4],
            'pid': datas[5]}

def update_project_db(name, pid, status):
    connection = connect_db()
    per = connection.cursor()
    per.execute("UPDATE projects SET pid = ?, status = ? WHERE name = ?", (pid, status, name,  ))
    connection.commit()
    connection.close()

def delete_project_db(name):
    connection = connect_db()
    per = connection.cursor()
    per.execute("DELETE FROM projects WHERE name = ?", (name, ))
    connection.commit()
    connection.close()