from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.config import pos_engine, admin_engine, AppBase, AdminBase 
from app.user_login import router as user_login_router
from app.user_crud import router as user_crud_router
from app.clients import router as client_router
from app.tickets import router as tickets_router
from app.packages import router as packages_router

AppBase.metadata.create_all(bind = pos_engine)
AdminBase.metadata.create_all(bind = admin_engine)

app = FastAPI()

@app.get("/")
def root():
    return "Hello World"

# CORS middleware to allow cross-origin requests if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_login_router)
app.include_router(user_crud_router)
app.include_router(client_router)
app.include_router(tickets_router)
app.include_router(packages_router)
