from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import FamilyMember, Vacation, Family
from app.services.vacation_service import VacationService, HolidayService
from datetime import date, datetime, timedelta
import calendar

from app.services.templates import templates

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.get("/", response_class=HTMLResponse)
async def calendar_view(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id: return RedirectResponse(url="/login", status_code=303)
    
    from app.services.family_service import get_family_members
    family_members = get_family_members(db, user_id)
    family = db.query(Family).filter(Family.owner_id == user_id).first()
    
    # Generate timeline days for the current year
    year = family.default_year
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    timeline_days = []
    months = []
    curr = start_date
    current_month = None
    
    while curr <= end_date:
        m_name = curr.strftime('%B')
        if m_name != current_month:
            current_month = m_name
            months.append({"name": m_name, "days": 0})
        
        months[-1]["days"] += 1
        
        timeline_days.append({
            "date": curr,
            "is_weekend": curr.weekday() >= 5,
            "name": curr.strftime('%a')[0],
            "is_first_of_month": curr.day == 1,
            "month_name": m_name
        })
        curr += timedelta(days=1)
    
    # Group holidays by member
    holidays_by_member = {}
    for member in family_members:
        holidays_by_member[member.id] = HolidayService.get_holidays(member.country, member.subdivision, year)
            
    return templates.TemplateResponse(request=request, name="calendar.html", context={
        "family": family,
        "family_members": family_members,
        "timeline_days": timeline_days,
        "months": months,
        "holidays_by_member": holidays_by_member
    })

@router.get("/add-vacation", response_class=HTMLResponse)
async def add_vacation_modal(request: Request, member_id: int = Query(None), db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    family = db.query(Family).filter(Family.owner_id == user_id).first()
    members = db.query(FamilyMember).filter(FamilyMember.family_id == family.id).all()
    return templates.TemplateResponse(request=request, name="modals/add_vacation.html", context={
        "members": members, 
        "selected_member_id": member_id
    })

@router.post("/add-vacation")
async def add_vacation(
    request: Request,
    member_id: int = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    title: str = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    # Verify the member belongs to the user's family
    member = db.query(FamilyMember).join(Family).filter(
        FamilyMember.id == member_id, 
        Family.owner_id == user_id
    ).first()
    
    if not member:
        return RedirectResponse(url="/calendar", status_code=303)
    
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    business_days = VacationService.calculate_business_days(
        start, end, member.country, member.subdivision, member.working_days
    )
    
    new_vac = Vacation(
        member_id=member_id,
        start_date=start,
        end_date=end,
        title=title,
        notes=notes,
        business_days_spent=business_days
    )
    db.add(new_vac)
    db.commit()
    
    referer = request.headers.get("referer", "/calendar")
    return RedirectResponse(url=referer, status_code=303)

@router.get("/edit-vacation/{vac_id}", response_class=HTMLResponse)
async def edit_vacation_modal(vac_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    vac = db.query(Vacation).join(FamilyMember).join(Family).filter(Vacation.id == vac_id, Family.owner_id == user_id).first()
    if not vac: return HTMLResponse("Trip not found")
    
    family = db.query(Family).filter(Family.owner_id == user_id).first()
    members = db.query(FamilyMember).filter(FamilyMember.family_id == family.id).all()
    
    return templates.TemplateResponse(request=request, name="modals/edit_vacation.html", context={
        "vacation": vac,
        "members": members
    })

@router.post("/update-vacation/{vac_id}")
async def update_vacation(
    vac_id: int,
    request: Request,
    member_id: int = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    title: str = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    # Verify the vacation belongs to the user
    vac = db.query(Vacation).join(FamilyMember).join(Family).filter(
        Vacation.id == vac_id, 
        Family.owner_id == user_id
    ).first()
    
    if not vac: return RedirectResponse(url="/calendar", status_code=303)
    
    # Verify the target member also belongs to the user
    member = db.query(FamilyMember).join(Family).filter(
        FamilyMember.id == member_id, 
        Family.owner_id == user_id
    ).first()
    
    if not member: return RedirectResponse(url="/calendar", status_code=303)
    
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    business_days = VacationService.calculate_business_days(
        start, end, member.country, member.subdivision, member.working_days
    )
    
    vac.member_id = member_id
    vac.start_date = start
    vac.end_date = end
    vac.title = title
    vac.notes = notes
    vac.business_days_spent = business_days
    
    db.commit()
    
    referer = request.headers.get("referer", "/calendar")
    return RedirectResponse(url=referer, status_code=303)

@router.delete("/vacation/{vac_id}")
async def delete_vacation(vac_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    vac = db.query(Vacation).join(FamilyMember).join(Family).filter(Vacation.id == vac_id, Family.owner_id == user_id).first()
    if vac:
        db.delete(vac)
        db.commit()
    return HTMLResponse(content="")
