from datetime import date

from flask import Blueprint, redirect, render_template, session

from app.db.database import SessionLocal
from app.models.models import Family, FamilyMember, Vacation
from app.services.family_service import get_family_members

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/dashboard")
def dashboard():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login", code=303)

    db = SessionLocal()
    try:
        family_members = get_family_members(db, user_id)

        family = db.query(Family).filter(Family.owner_id == user_id).first()
        if not family:
            family = Family(name="Our Family", owner_id=user_id)
            db.add(family)
            db.commit()
            db.refresh(family)

        today = date.today()
        upcoming_vacations = (
            db.query(Vacation)
            .join(FamilyMember)
            .filter(FamilyMember.family_id == family.id, Vacation.start_date >= today)
            .order_by(Vacation.start_date)
            .limit(5)
            .all()
        )

        return render_template(
            "dashboard.html",
            family=family,
            total_members=len(family_members),
            upcoming_vacations=upcoming_vacations,
            members=family_members,
            family_members=family_members,
        )
    finally:
        db.close()
