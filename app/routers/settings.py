from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Family

from app.services.templates import templates

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("/", response_class=HTMLResponse)
async def settings_view(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id: return RedirectResponse(url="/login", status_code=303)
    
    from app.services.family_service import get_family_members
    family_members = get_family_members(db, user_id)
    
    family = db.query(Family).filter(Family.owner_id == user_id).first()
    return templates.TemplateResponse(request=request, name="settings.html", context={
        "family": family,
        "family_members": family_members
    })

@router.post("/update")
async def update_settings(
    request: Request,
    name: str = Form(...),
    country: str = Form(...),
    year: int = Form(...),
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    family = db.query(Family).filter(Family.owner_id == user_id).first()
    
    family.name = name
    family.default_country = country
    family.default_year = year
    db.commit()
    
    return RedirectResponse(url="/settings", status_code=303)
