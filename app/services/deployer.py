import signal
import subprocess
import os
import socket
import time

from app.core.state import projects

def port_is_open(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('127.0.0.1', port))
    return result == 0

def deploy_project(name):
    project = projects.get(name)
    if not project:
        return {'Ошибка': 'Проект не найден'}
    if project['status'] == 'running':
        return {'Ошибка': 'Проект уже запущен'}
    process = subprocess.Popen(['python', '-m', 'http.server', '8000'])
    project['pid'] = process.pid
    project['status'] = 'starting'
    time.sleep(2)
    if port_is_open(8000):
        project['status'] = 'running'
    else:
        project['status'] = 'error'
    return {'status' : project['status']}

def stop_project(name):
    project = projects.get(name)
    if not project:
        return {'Ошибка': 'Проект не найден'}
    if project['status'] != 'running':
        return {'Ошибка': 'Проект не запущен'}
    os.kill(projects[name]['pid'], signal.SIGTERM)
    time.sleep(2)
    project['pid'] = None
    project['status'] = 'stopped'
    return {'status' : project['status']}


def get_status(name):
    project = projects.get(name)
    if not project:
        return {'Ошибка': 'Проект не найден'}
    return {'status' : project['status']}