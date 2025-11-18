from fastapi import FastAPI
from src.books.routes import book_router
from src.auth.routes import auth_router
from contextlib import asynccontextmanager
from src.db.main import init_db, close_db, health_check

@asynccontextmanager
async def life_span(app: FastAPI):
    print("Starting up server ...")
    await init_db()
    
    # Check database health
    if await health_check():
        print("Database connection healthy")
    else:
        print("Database connection failed")
    
    yield
    
    print("Shutting down server ...")
    await close_db()


version = "v1"

app = FastAPI(
    title="Bookly",
    description="A simple book management API",
    version=version
    
)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])

app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])