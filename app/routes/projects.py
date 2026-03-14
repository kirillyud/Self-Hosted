from fastapi import APIRouter, HTTPException
from app.core.state import projects
from pydantic import BaseModel
from database.database import add_project_db
router = APIRouter()

class ProjectAddItems(BaseModel):
    name: str
    port: int
    command: str
    repo_url: str

@router.post('/projects')
def add_projects(new_project: ProjectAddItems):
    if new_project.name not in projects:
        add_project_db(
            new_project.name,
            new_project.repo_url,
            new_project.command,
            new_project.port
        )
        return {'success': True}
    else:
        raise HTTPException(status_code=400, detail='Проект с таким названием уже существует')

@router.get('/projects')
def show_projects():
    return projects

@router.get('/projects/{project_name}')
def get_projects(project_name):
    for project in projects:
        if project_name == project:
            return projects[project_name]
    return HTTPException(status_code=404, detail='Проект с таким названием не найден')