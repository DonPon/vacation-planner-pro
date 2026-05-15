from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import FamilyMember, Vacation, Family
from datetime import date
from app.services.templates import templates

router = APIRouter(tags=["dashboard"])

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    
    from app.services.family_service import get_family_members
    family_members = get_family_members(db, user_id)
    
    family = db.query(Family).filter(Family.owner_id == user_id).first()
    if not family:
        # Auto-create a family if it doesn't exist
        family = Family(name="Our Family", owner_id=user_id)
        db.add(family)
        db.commit()
        db.refresh(family)
    
    today = date.today()
    upcoming_vacations = db.query(Vacation).join(FamilyMember).filter(
        FamilyMember.family_id == family.id,
        Vacation.start_date >= today
    ).order_by(Vacation.start_date).limit(5).all()
    
    return templates.TemplateResponse(request=request, name="dashboard.html", context={
        "family": family,
        "total_members": len(family_members),
        "upcoming_vacations": upcoming_vacations,
        "members": family_members,
        "family_members": family_members
    })
