from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import FamilyMember, Family
import uuid

from app.services.templates import templates

router = APIRouter(prefix="/family", tags=["family"])

@router.get("/", response_class=HTMLResponse)
async def family_list(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id: return RedirectResponse(url="/login", status_code=303)
    
    from app.services.family_service import get_family_members
    family_members = get_family_members(db, user_id)
    family = db.query(Family).filter(Family.owner_id == user_id).first()
    
    return templates.TemplateResponse(request=request, name="family.html", context={
        "members": family_members, 
        "family": family,
        "family_members": family_members
    })

@router.get("/add-member", response_class=HTMLResponse)
async def add_member_modal(request: Request):
    # Supported countries and their subdivisions for the 'holidays' package
    country_data = {
        "CH": {
            "name": "Switzerland",
            "subdivisions": {
                "AG": "Aargau", "AR": "Appenzell Ausserrhoden", "AI": "Appenzell Innerrhoden", "BL": "Basel-Landschaft",
                "BS": "Basel-Stadt", "BE": "Bern", "FR": "Fribourg", "GE": "Geneva", "GL": "Glarus", "GR": "Graubünden",
                "JU": "Jura", "LU": "Lucerne", "NE": "Neuchâtel", "NW": "Nidwalden", "OW": "Obwalden", "SH": "Schaffhausen",
                "SZ": "Schwyz", "SO": "Solothurn", "SG": "St. Gallen", "TG": "Thurgau", "TI": "Ticino", "UR": "Uri",
                "VS": "Valais", "VD": "Vaud", "ZG": "Zug", "ZH": "Zurich"
            }
        },
        "US": {
            "name": "United States",
            "subdivisions": {
                "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
                "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
                "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
                "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
                "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
                "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
                "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
                "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
                "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"
            }
        },
        "MX": {"name": "Mexico", "subdivisions": {}},
        "DE": {
            "name": "Germany",
            "subdivisions": {
                "BW": "Baden-Württemberg", "BY": "Bayern", "BE": "Berlin", "BB": "Brandenburg", "HB": "Bremen",
                "HH": "Hamburg", "HE": "Hessen", "MV": "Mecklenburg-Vorpommern", "NI": "Niedersachsen", "NW": "Nordrhein-Westfalen",
                "RP": "Rheinland-Pfalz", "SL": "Saarland", "SN": "Sachsen", "ST": "Sachsen-Anhalt", "SH": "Schleswig-Holstein", "TH": "Thüringen"
            }
        },
        "ES": {
            "name": "Spain",
            "subdivisions": {
                "AN": "Andalucía", "AR": "Aragón", "AS": "Asturias", "CB": "Cantabria", "CE": "Ceuta", "CL": "Castilla y León",
                "CM": "Castilla-La Mancha", "CN": "Canarias", "CT": "Cataluña", "EX": "Extremadura", "GA": "Galicia",
                "IB": "Islas Baleares", "MC": "Murcia", "MD": "Madrid", "ML": "Melilla", "NC": "Navarra", "PV": "País Vasco", "RI": "La Rioja", "VC": "Valenciana"
            }
        },
        "FR": {"name": "France", "subdivisions": {}},
        "IT": {"name": "Italy", "subdivisions": {}},
        "GB": {"name": "United Kingdom", "subdivisions": {"ENG": "England", "SCT": "Scotland", "WLS": "Wales", "NIR": "Northern Ireland"}}
    }
    return templates.TemplateResponse(request=request, name="modals/add_member.html", context={"country_data": country_data})

@router.post("/add-member")
async def add_member(
    request: Request,
    name: str = Form(...),
    country: str = Form(...),
    subdivision: str = Form(None),
    allowance: float = Form(...),
    working_days: int = Form(...),
    color: str = Form(...),
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    family = db.query(Family).filter(Family.owner_id == user_id).first()
    
    new_member = FamilyMember(
        name=name,
        family_id=family.id,
        country=country,
        subdivision=subdivision if subdivision else None,
        vacation_allowance=allowance,
        working_days=working_days,
        color=color
    )
    db.add(new_member)
    db.commit()
    
    return RedirectResponse(url="/family", status_code=303)

@router.delete("/{member_id}")
async def delete_member(member_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    # Verify ownership
    member = db.query(FamilyMember).join(Family).filter(FamilyMember.id == member_id, Family.owner_id == user_id).first()
    if member:
        db.delete(member)
        db.commit()
    return HTMLResponse(content="") # HTMX will remove the row
    
@router.get("/{member_id}")
async def member_details(member_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    member = db.query(FamilyMember).join(Family).filter(FamilyMember.id == member_id, Family.owner_id == user_id).first()
    if not member: return RedirectResponse(url="/family", status_code=303)
    
    from app.services.family_service import get_family_members
    family_members = get_family_members(db, user_id)
    
    # Calculate balance
    spent = sum(v.business_days_spent for v in member.vacations)
    member.remaining_balance = member.vacation_allowance - spent
    
    return templates.TemplateResponse(request=request, name="person.html", context={
        "member": member,
        "family_members": family_members
    })
