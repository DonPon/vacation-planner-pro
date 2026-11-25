import os
from datetime import date

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

from app.db.database import Base, engine
from app.routers.auth import auth_bp
from app.routers.calendar import calendar_bp
from app.routers.dashboard import dashboard_bp
from app.routers.family import family_bp
from app.routers.settings import settings_bp


def normalize_prefix(value):
    prefix = (value or "").strip()
    if not prefix:
        return ""
    if not prefix.startswith("/"):
        prefix = "/" + prefix
    if prefix != "/":
        prefix = prefix.rstrip("/")
    return prefix


APP_PREFIX = normalize_prefix(os.environ.get("APP_PREFIX", ""))

Base.metadata.create_all(bind=engine)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.config["SESSION_COOKIE_NAME"] = os.environ.get(
    "SESSION_COOKIE_NAME", "vacationplanner_session"
)
app.config["APPLICATION_ROOT"] = APP_PREFIX or "/"
app.url_map.strict_slashes = False
app.jinja_env.globals["date"] = date

# Behind a proxy that strips the path prefix, set PREFIX_FROM_HEADER=1 and have
# the proxy send X-Forwarded-Prefix. Otherwise the prefix is handled by the
# DispatcherMiddleware in wsgi.py.
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_prefix=1 if os.environ.get("PREFIX_FROM_HEADER") == "1" else 0,
)

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(family_bp, url_prefix="/family")
app.register_blueprint(calendar_bp, url_prefix="/calendar")
app.register_blueprint(settings_bp, url_prefix="/settings")


@app.context_processor
def navigation_helpers():
    def is_active(endpoint, **values):
        target = url_for(endpoint, **values)
        if request.script_root and target.startswith(request.script_root):
            target = target[len(request.script_root) :]
        target = target.rstrip("/") or "/"
        path = request.path.rstrip("/") or "/"
        return path == target or path.startswith(target.rstrip("/") + "/")

    return {"is_active": is_active}


@app.get("/")
def root():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"), code=303)
    return render_template("landing.html")
