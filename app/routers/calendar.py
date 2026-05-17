from datetime import date, datetime, timedelta

from flask import Blueprint, redirect, render_template, request, session

from app.db.database import SessionLocal
from app.models.models import Family, FamilyMember, Vacation
from app.services.family_service import get_family_members
from app.services.vacation_service import HolidayService, VacationService

calendar_bp = Blueprint("calendar", __name__)


@calendar_bp.get("/")
def calendar_view():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login", code=303)

    db = SessionLocal()
    try:
        family_members = get_family_members(db, user_id)
        family = db.query(Family).filter(Family.owner_id == user_id).first()

        year = family.default_year
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        timeline_days = []
        months = []
        curr = start_date
        current_month = None

        while curr <= end_date:
            month_name = curr.strftime("%B")
            if month_name != current_month:
                current_month = month_name
                months.append({"name": month_name, "days": 0})

            months[-1]["days"] += 1
            timeline_days.append(
                {
                    "date": curr,
                    "is_weekend": curr.weekday() >= 5,
                    "name": curr.strftime("%a")[0],
                    "is_first_of_month": curr.day == 1,
                    "month_name": month_name,
                }
            )
            curr += timedelta(days=1)

        holidays_by_member = {
            member.id: HolidayService.get_holidays(member.country, member.subdivision, year)
            for member in family_members
        }

        return render_template(
            "calendar.html",
            family=family,
            family_members=family_members,
            timeline_days=timeline_days,
            months=months,
            holidays_by_member=holidays_by_member,
        )
    finally:
        db.close()


@calendar_bp.get("/add-vacation")
def add_vacation_modal():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login", code=303)

    db = SessionLocal()
    try:
        family = db.query(Family).filter(Family.owner_id == user_id).first()
        members = db.query(FamilyMember).filter(FamilyMember.family_id == family.id).all()
        selected_member_id = request.args.get("member_id", type=int)
        return render_template(
            "modals/add_vacation.html",
            members=members,
            selected_member_id=selected_member_id,
        )
    finally:
        db.close()


@calendar_bp.post("/add-vacation")
def add_vacation():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login", code=303)

    db = SessionLocal()
    try:
        member_ids = [int(member_id) for member_id in request.form.getlist("member_ids")]
        if not member_ids:
            return redirect("/calendar", code=303)

        members = (
            db.query(FamilyMember)
            .join(Family)
            .filter(FamilyMember.id.in_(member_ids), Family.owner_id == user_id)
            .all()
        )
        members_by_id = {member.id: member for member in members}
        valid_member_ids = [member_id for member_id in member_ids if member_id in members_by_id]
        if not valid_member_ids:
            return redirect("/calendar", code=303)

        start = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
        end = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()
        title = request.form.get("title") or None
        notes = request.form.get("notes") or None

        for member_id in valid_member_ids:
            member = members_by_id[member_id]
            business_days = VacationService.calculate_business_days(
                start, end, member.country, member.subdivision, member.working_days
            )
            db.add(
                Vacation(
                    member_id=member_id,
                    start_date=start,
                    end_date=end,
                    title=title,
                    notes=notes,
                    business_days_spent=business_days,
                )
            )
        db.commit()

        return redirect(request.headers.get("referer", "/calendar"), code=303)
    finally:
        db.close()


@calendar_bp.get("/edit-vacation/<int:vac_id>")
def edit_vacation_modal(vac_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login", code=303)

    db = SessionLocal()
    try:
        vacation = (
            db.query(Vacation)
            .join(FamilyMember)
            .join(Family)
            .filter(Vacation.id == vac_id, Family.owner_id == user_id)
            .first()
        )
        if not vacation:
            return "Trip not found"

        family = db.query(Family).filter(Family.owner_id == user_id).first()
        members = db.query(FamilyMember).filter(FamilyMember.family_id == family.id).all()
        return render_template("modals/edit_vacation.html", vacation=vacation, members=members)
    finally:
        db.close()


@calendar_bp.post("/update-vacation/<int:vac_id>")
def update_vacation(vac_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login", code=303)

    db = SessionLocal()
    try:
        vacation = (
            db.query(Vacation)
            .join(FamilyMember)
            .join(Family)
            .filter(Vacation.id == vac_id, Family.owner_id == user_id)
            .first()
        )
        if not vacation:
            return redirect("/calendar", code=303)

        member_id = int(request.form["member_id"])
        member = (
            db.query(FamilyMember)
            .join(Family)
            .filter(FamilyMember.id == member_id, Family.owner_id == user_id)
            .first()
        )
        if not member:
            return redirect("/calendar", code=303)

        start = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
        end = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()
        business_days = VacationService.calculate_business_days(
            start, end, member.country, member.subdivision, member.working_days
        )

        vacation.member_id = member_id
        vacation.start_date = start
        vacation.end_date = end
        vacation.title = request.form.get("title") or None
        vacation.notes = request.form.get("notes") or None
        vacation.business_days_spent = business_days
        db.commit()

        return redirect(request.headers.get("referer", "/calendar"), code=303)
    finally:
        db.close()


@calendar_bp.delete("/vacation/<int:vac_id>")
def delete_vacation(vac_id):
    user_id = session.get("user_id")
    db = SessionLocal()
    try:
        vacation = (
            db.query(Vacation)
            .join(FamilyMember)
            .join(Family)
            .filter(Vacation.id == vac_id, Family.owner_id == user_id)
            .first()
        )
        if vacation:
            db.delete(vacation)
            db.commit()
        return ""
    finally:
        db.close()
