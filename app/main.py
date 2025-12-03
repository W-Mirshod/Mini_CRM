from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import operators, sources, contacts, view

app = FastAPI(title="Mini-CRM Lead Distribution")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(operators.router)
app.include_router(sources.router)
app.include_router(contacts.router)
app.include_router(view.router)

@app.get("/")
async def root():
    return {"message": "Mini-CRM is running"}
