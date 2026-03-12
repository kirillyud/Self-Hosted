import signal
import subprocess
import os
import socket
import time
import shlex
import pathlib
import shutil

from app.core.state import projects

def port_is_open(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def deploy_project(name):
    project = projects.get(name)
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
    project['pid'] = process.pid
    project['status'] = 'starting'
    time.sleep(2)
    if process.poll() != None:
        project['status'] = 'error'
        return {'Ошибка': 'Ошибка при запуске'}
    else:
        if port_is_open(project['port']):
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
    if port_is_open(project['port']):
        os.kill(projects[name]['pid'], signal.SIGKILL)
        time.sleep(2)
        if port_is_open(project['port']):
            project['status'] = 'error'
        else:
            project['pid'] = None
            project['status'] = 'stopped'
    else:
        project['pid'] = None
        project['status'] = 'stopped'
    return {'status' : project['status']}


def get_status(name):
    project = projects.get(name)
    if not project:
        return {'Ошибка': 'Проект не найден'}
    return {'status' : project['status']}