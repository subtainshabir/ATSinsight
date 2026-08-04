from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config.settings import settings
from app.routes import upload_routes, analysis_routes, enhancement_routes

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(upload_routes.router)
app.include_router(analysis_routes.router)
app.include_router(enhancement_routes.router)

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "app_name": settings.app_name}
    )