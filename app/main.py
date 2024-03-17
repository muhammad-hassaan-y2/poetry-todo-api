from contextlib import asynccontextmanager
from typing import Optional, Annotated
from settings import DATABASE_URL, TEST_DATABASE_URL
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import FastAPI, Depends

# Define a Todo model
class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(index=True)

# Create database engine
engine = create_engine(str(DATABASE_URL))

# Create database tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Asynchronous context manager to create database tables before starting the application
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    servers=[
        {
            "url": "http://0.0.0.0:8000", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        }
        ])

def get_session():
    with Session(engine) as session:
        yield session


@app.get("/")
def read_root():
    return {"Muhammad": "Hassaan"}

@app.post("/todos/", response_model=Todo)
def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)]):
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo


@app.get("/todos/", response_model=list[Todo])
def read_todos(session: Annotated[Session, Depends(get_session)]):
        todos = session.exec(select(Todo)).all()
        return todos