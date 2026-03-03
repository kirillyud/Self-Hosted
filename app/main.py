from fastapi import FastAPI
import uvicorn

from app.routes.projects import router as projects_router

app = FastAPI()

@app.get('/')
def start_page():
    return 'hi there'

app.include_router(projects_router)

if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)
