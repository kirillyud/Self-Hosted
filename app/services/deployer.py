import signal
import subprocess
import os
import socket
import time
import shlex
import pathlib
import shutil

from database.database import get_project_db, update_project_db, delete_project_db

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
        return {'error': 'Проект не найден'}
    if project['status'] == 'running':
        return {'error': 'Проект уже запущен'}
    if path.exists():
        if path.is_dir() and pathlib.Path(f'projects/{name}/.git').exists():
            shutil.rmtree(path, ignore_errors=True)
            subprocess.run(['git', 'clone', project['repo_url'], path])
    else:
        subprocess.run(['git', 'clone', project['repo_url'], path])
    with open(f'logs/{name}.log', 'w') as process_out:
        process = subprocess.Popen(shlex.split(project['command']), cwd=path, stdout=process_out, stderr=process_out)
    update_project_db(name, process.pid, "starting")
    time.sleep(2)
    if process.poll() != None:
        update_project_db(name, process.pid, "error")
        return {'error': 'Ошибка при запуске'}
    else:
        if port_is_open(project['port']):
            update_project_db(name, process.pid, "running")
            return {'status': 'running'}
        else:
            update_project_db(name, process.pid, "error")
            return {'error': 'Ошибка при запуске'}

def stop_project(name):
    project = get_project_db(name)
    if not project:
        return {'error': 'Проект не найден'}
    if project['status'] != 'running':
        return {'error': 'Проект не запущен'}
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
        return {'error': 'Проект не найден'}
    return {'status' : project['status']}

def delete_project_service(name):
    project = get_project_db(name)
    path = pathlib.Path(f'projects/{name}')
    if project['status'] == 'running':
        stop_project(name)
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
            delete_project_db(name)
            return {'success': True}
        return {'success': False}
    else:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
            delete_project_db(name)
            return {'success': True}
        return {'success': False}