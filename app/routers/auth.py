from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User

from app.services.templates import templates

router = APIRouter(tags=["auth"])

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@router.post("/register")
async def register(
    request: Request, 
    email: str = Form(...), 
    password: str = Form(...), 
    family_name: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if user already exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return templates.TemplateResponse(request=request, name="register.html", context={"error": "Email already registered"})
    
    # Create user
    new_user = User(email=email, password=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create initial family
    from app.models.models import Family
    new_family = Family(name=family_name, owner_id=new_user.id)
    db.add(new_family)
    db.commit()
    
    request.session["user_id"] = new_user.id
    return RedirectResponse(url="/dashboard", status_code=303)

@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or user.password != password:
        return templates.TemplateResponse(request=request, name="login.html", context={"error": "Invalid email or password"})
    
    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=303)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
