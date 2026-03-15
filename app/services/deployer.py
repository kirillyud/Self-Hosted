import signal
import subprocess
import os
import socket
import time
import shlex
import pathlib
import shutil

from app.core.state import projects
from database.database import get_project_db, update_project_db

def port_is_open(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def deploy_project(name):
    project = get_project_db(name)
    path = pathlib.Path(f'projects/{name}')
    if not project:
        return {'Ошибка': 'Проект не найден'}
    if project['status'] == 'running':
        return {'Ошибка': 'Проект уже запущен'}
    if path.exists():
        if path.is_dir() and pathlib.Path(f'projects/{name}/.git').exists():
            shutil.rmtree(path, ignore_errors=True)
            subprocess.run(['git', 'clone', project['repo_url'], path])
    else:
        subprocess.run(['git', 'clone', project['repo_url'], path])
    process = subprocess.Popen(shlex.split(project['command']), cwd=path)
    update_project_db(name, process.pid, "starting")
    time.sleep(2)
    if process.poll() != None:
        update_project_db(name, process.pid, "error")
        return {'Ошибка': 'Ошибка при запуске'}
    else:
        if port_is_open(project['port']):
            update_project_db(name, process.pid, "running")
            return {'status': 'running'}
        else:
            update_project_db(name, process.pid, "error")
            return {'Ошибка': 'Ошибка при запуске'}

def stop_project(name):
    project = get_project_db(name)
    if not project:
        return {'Ошибка': 'Проект не найден'}
    if project['status'] != 'running':
        return {'Ошибка': 'Проект не запущен'}
    os.kill(project['pid'], signal.SIGTERM)
    time.sleep(2)
    if port_is_open(project['port']):
        os.kill(project['pid'], signal.SIGKILL)
        time.sleep(2)
        if port_is_open(project['port']):
            update_project_db(name, project['pid'], "error")
            return {'status': 'error'}
        else:
            update_project_db(name, None, "stopped")
            return {'status': 'stopped'}
    else:
        update_project_db(name, None, "stopped")
        return {'status': 'stopped'}


def get_status(name):
    project = get_project_db(name)
    if not project:
        return {'Ошибка': 'Проект не найден'}
    return {'status' : project['status']}