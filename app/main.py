from fastapi import FastAPI
import uvicorn

from app.routes.projects import router as projects_router
from app.routes.deploy import router as control_router
from database.database import init_db
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

@app.get('/')
def start_page():
    return 'hi there'

app.include_router(projects_router)
app.include_router(control_router)

if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)
