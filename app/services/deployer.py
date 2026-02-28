import subprocess
import os
import socket

from app.core.state import projects

def port_is_open(port):
    ...

def deploy_project(name):
    project = projects.get(name)
    if not project:
        return {'Ошибка': 'Проект не найден'}
    if project['status'] == 'running':
        return {'Ошибка': 'Проект уже запущен'}







def stop_project(name):
    ...

def get_status(name):
    ...