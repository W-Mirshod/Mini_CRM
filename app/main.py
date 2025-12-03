from fastapi import FastAPI
from .routers import operators, sources, contacts, view

app = FastAPI(title="Mini-CRM Lead Distribution")

app.include_router(operators.router)
app.include_router(sources.router)
app.include_router(contacts.router)
app.include_router(view.router)

@app.get("/")
async def root():
    return {"message": "Mini-CRM is running"}
