from datetime import date

from flask import Flask, redirect, render_template, session

from app.db.database import Base, engine
from app.routers.auth import auth_bp
from app.routers.calendar import calendar_bp
from app.routers.dashboard import dashboard_bp
from app.routers.family import family_bp
from app.routers.settings import settings_bp

Base.metadata.create_all(bind=engine)

app = Flask(__name__)
app.secret_key = "super-secret-key"
app.url_map.strict_slashes = False
app.jinja_env.globals["date"] = date

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(family_bp, url_prefix="/family")
app.register_blueprint(calendar_bp, url_prefix="/calendar")
app.register_blueprint(settings_bp, url_prefix="/settings")


@app.get("/")
def root():
    if "user_id" in session:
        return redirect("/dashboard", code=303)
    return render_template("landing.html")
