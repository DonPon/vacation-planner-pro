from flask import Blueprint, redirect, render_template, request, session

from app.db.database import SessionLocal
from app.models.models import Family
from app.services.family_service import get_family_members

settings_bp = Blueprint("settings", __name__)


@settings_bp.get("/")
def settings_view():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login", code=303)

    db = SessionLocal()
    try:
        family_members = get_family_members(db, user_id)
        family = db.query(Family).filter(Family.owner_id == user_id).first()
        return render_template("settings.html", family=family, family_members=family_members)
    finally:
        db.close()


@settings_bp.post("/update")
def update_settings():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login", code=303)

    db = SessionLocal()
    try:
        family = db.query(Family).filter(Family.owner_id == user_id).first()
        family.name = request.form["name"]
        family.default_country = request.form["country"]
        family.default_year = int(request.form["year"])
        db.commit()
        return redirect("/settings", code=303)
    finally:
        db.close()
