import os
import sys
from werkzeug.middleware.dispatcher import DispatcherMiddleware

project_home = os.path.dirname(os.path.abspath(__file__))

if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app.main import APP_PREFIX, app as application

# Default deployment: the proxy forwards the full path (e.g.
# /vacation-planner/dashboard) and this middleware strips the prefix.
# If the proxy strips the prefix itself, set PREFIX_FROM_HEADER=1 instead.
def not_found(environ, start_response):
    start_response("404 NOT FOUND", [("Content-Type", "text/plain")])
    return [b"Not Found"]


if APP_PREFIX and os.environ.get("PREFIX_FROM_HEADER") != "1":
    application = DispatcherMiddleware(not_found, {APP_PREFIX: application})
