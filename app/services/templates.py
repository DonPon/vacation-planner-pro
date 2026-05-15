from fastapi.templating import Jinja2Templates
from datetime import date

templates = Jinja2Templates(directory="app/templates")
templates.env.globals["date"] = date
