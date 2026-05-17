from flask import Blueprint, redirect, render_template, request, session

from app.db.database import SessionLocal
from app.models.models import Family, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/login")
def login_page():
    return render_template("login.html")


@auth_bp.get("/register")
def register_page():
    return render_template("register.html")


@auth_bp.post("/register")
def register():
    db = SessionLocal()
    try:
        email = request.form["email"]
        password = request.form["password"]
        family_name = request.form["family_name"]

        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return render_template("register.html", error="Email already registered")

        new_user = User(email=email, password=password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        new_family = Family(name=family_name, owner_id=new_user.id)
        db.add(new_family)
        db.commit()

        session["user_id"] = new_user.id
        return redirect("/dashboard", code=303)
    finally:
        db.close()


@auth_bp.post("/login")
def login():
    db = SessionLocal()
    try:
        email = request.form["email"]
        password = request.form["password"]

        user = db.query(User).filter(User.email == email).first()
        if not user or user.password != password:
            return render_template("login.html", error="Invalid email or password")

        session["user_id"] = user.id
        return redirect("/dashboard", code=303)
    finally:
        db.close()


@auth_bp.get("/logout")
def logout():
    session.clear()
    return redirect("/", code=303)
