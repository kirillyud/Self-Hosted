from fastapi import APIRouter, HTTPException
from app.core.state import projects
from pydantic import BaseModel

router = APIRouter()

class ProjectAddItems(BaseModel):
    name: str
    port: int
    command: str

@router.post('/projects')
async def add_projects(new_project: ProjectAddItems):
    if new_project.name not in projects:
        projects[new_project.name] = {"status": "stopped",
                                      "pid": None,
                                      "port": new_project.port,
                                      "command": new_project.command}
        return {'success': True}
    else:
        raise HTTPException(status_code=400, detail='Уже существует проект с таким названием')

@router.get('/projects')
def show_projects():
    return projects

@router.get('/projects/{project_name}')
def get_projects(project_name):
    for project in projects:
        if project_name == project:
            return projects[project_name]
        return HTTPException(status_code=404, detail='Проект с таким названием не найден')