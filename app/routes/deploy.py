from fastapi import APIRouter

from app.services.deployer import deploy_project, stop_project, get_status

router = APIRouter()

@router.post('/deploy/{name}')
def deploy(name):
    return deploy_project(name)

@router.post('/stop/{name}')
def stop(name):
    return stop_project(name)

@router.post('/status/{name}')
def status(name):
    return get_status(name)
