from flask import Blueprint, redirect, render_template, request, session

from app.db.database import SessionLocal
from app.models.models import Family, FamilyMember
from app.services.family_service import get_family_members

family_bp = Blueprint("family", __name__)


def country_data():
    return {
        "CH": {
            "name": "Switzerland",
            "subdivisions": {
                "AG": "Aargau", "AR": "Appenzell Ausserrhoden", "AI": "Appenzell Innerrhoden", "BL": "Basel-Landschaft",
                "BS": "Basel-Stadt", "BE": "Bern", "FR": "Fribourg", "GE": "Geneva", "GL": "Glarus", "GR": "Graubunden",
                "JU": "Jura", "LU": "Lucerne", "NE": "Neuchatel", "NW": "Nidwalden", "OW": "Obwalden", "SH": "Schaffhausen",
                "SZ": "Schwyz", "SO": "Solothurn", "SG": "St. Gallen", "TG": "Thurgau", "TI": "Ticino", "UR": "Uri",
                "VS": "Valais", "VD": "Vaud", "ZG": "Zug", "ZH": "Zurich"
            },
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
            },
        },
        "MX": {"name": "Mexico", "subdivisions": {}},
        "DE": {
            "name": "Germany",
            "subdivisions": {
                "BW": "Baden-Wurttemberg", "BY": "Bayern", "BE": "Berlin", "BB": "Brandenburg", "HB": "Bremen",
                "HH": "Hamburg", "HE": "Hessen", "MV": "Mecklenburg-Vorpommern", "NI": "Niedersachsen", "NW": "Nordrhein-Westfalen",
                "RP": "Rheinland-Pfalz", "SL": "Saarland", "SN": "Sachsen", "ST": "Sachsen-Anhalt", "SH": "Schleswig-Holstein", "TH": "Thuringen"
            },
        },
        "ES": {
            "name": "Spain",
            "subdivisions": {
                "AN": "Andalucia", "AR": "Aragon", "AS": "Asturias", "CB": "Cantabria", "CE": "Ceuta", "CL": "Castilla y Leon",
                "CM": "Castilla-La Mancha", "CN": "Canarias", "CT": "Cataluna", "EX": "Extremadura", "GA": "Galicia",
                "IB": "Islas Baleares", "MC": "Murcia", "MD": "Madrid", "ML": "Melilla", "NC": "Navarra", "PV": "Pais Vasco", "RI": "La Rioja", "VC": "Valenciana"
            },
        },
        "FR": {"name": "France", "subdivisions": {}},
        "IT": {"name": "Italy", "subdivisions": {}},
        "GB": {"name": "United Kingdom", "subdivisions": {"ENG": "England", "SCT": "Scotland", "WLS": "Wales", "NIR": "Northern Ireland"}},
    }


@family_bp.get("/")
def family_list():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login", code=303)

    db = SessionLocal()
    try:
        family_members = get_family_members(db, user_id)
        family = db.query(Family).filter(Family.owner_id == user_id).first()
        return render_template("family.html", members=family_members, family=family, family_members=family_members)
    finally:
        db.close()


@family_bp.get("/add-member")
def add_member_modal():
    return render_template("modals/add_member.html", country_data=country_data())


@family_bp.post("/add-member")
def add_member():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login", code=303)

    db = SessionLocal()
    try:
        family = db.query(Family).filter(Family.owner_id == user_id).first()
        new_member = FamilyMember(
            name=request.form["name"],
            family_id=family.id,
            country=request.form["country"],
            subdivision=request.form.get("subdivision") or None,
            vacation_allowance=float(request.form["allowance"]),
            working_days=int(request.form["working_days"]),
            color=request.form["color"],
        )
        db.add(new_member)
        db.commit()
        return redirect("/family", code=303)
    finally:
        db.close()


@family_bp.delete("/<int:member_id>")
def delete_member(member_id):
    user_id = session.get("user_id")
    db = SessionLocal()
    try:
        member = (
            db.query(FamilyMember)
            .join(Family)
            .filter(FamilyMember.id == member_id, Family.owner_id == user_id)
            .first()
        )
        if member:
            db.delete(member)
            db.commit()
        return ""
    finally:
        db.close()


@family_bp.get("/<int:member_id>")
def member_details(member_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login", code=303)

    db = SessionLocal()
    try:
        member = (
            db.query(FamilyMember)
            .join(Family)
            .filter(FamilyMember.id == member_id, Family.owner_id == user_id)
            .first()
        )
        if not member:
            return redirect("/family", code=303)

        family_members = get_family_members(db, user_id)
        spent = sum(v.business_days_spent for v in member.vacations)
        member.remaining_balance = member.vacation_allowance - spent

        return render_template("person.html", member=member, family_members=family_members)
    finally:
        db.close()
