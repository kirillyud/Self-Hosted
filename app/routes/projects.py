from fastapi import APIRouter, HTTPException
from app.core.state import projects
from pydantic import BaseModel
from database.database import add_project_db, get_projects_db, get_project_db, delete_project_db
from app.services.deployer import get_status
router = APIRouter()

class ProjectAddItems(BaseModel):
    name: str
    port: int
    command: str
    repo_url: str

@router.post('/projects')
def add_projects(new_project: ProjectAddItems):
    return add_project_db(
            new_project.name,
            new_project.repo_url,
            new_project.command,
            new_project.port
    )


@router.get('/projects')
def show_projects():
    return get_projects_db()

@router.get('/projects/{project_name}')
def get_projects(project_name):
    data = get_project_db(project_name)
    if data:
        return data
    return HTTPException(status_code=404, detail='Проект с таким названием не найден')

@router.delete('/projects/{project_name}')
def delete_project(project_name):
    if get_status(project_name) != 'running':
        delete_project_db(project_name)
        return {'success': True}
    else:
        return {'Ошибка': 'Проект запущен'}