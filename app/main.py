from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel

app = FastAPI()

projects = {}

@app.get('/')
def start_page():
    return 'hi there'

class ProjectAddItems(BaseModel):
    name: str
    port: int
    command: str

@app.post('/projects')
async def add_projects(new_project: ProjectAddItems):
    if new_project.name not in projects:
        projects[new_project.name] = {"status": "stopped",
                                      "pid": None,
                                      "port": new_project.port,
                                      "command": new_project.command}
        return {'success': True}
    else:
        raise HTTPException(status_code=400, detail='Уже существует проект с таким названием')

@app.get('/projects')
def show_projects():
    return projects

@app.get('/projects/{project_name}')
def get_projects(project_name):
    for project in projects:
        if project_name == project:
            return projects[project_name]
        return HTTPException(status_code=404, detail='Проект с таким названием не найден')

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
