from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from app.db.database import engine, Base, get_db
from app.routers import auth, dashboard, family, calendar, settings
from fastapi.responses import RedirectResponse, HTMLResponse

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Family Vacation Planner")

# Session management
app.add_middleware(SessionMiddleware, secret_key="super-secret-key", session_cookie="family_planner_session")

# Static files & Templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if "user_id" in request.session:
        return RedirectResponse(url="/dashboard", status_code=303)
    from app.services.templates import templates
    return templates.TemplateResponse(request=request, name="landing.html")

# Include routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(family.router)
app.include_router(calendar.router)
app.include_router(settings.router)
