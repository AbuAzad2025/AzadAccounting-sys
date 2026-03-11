import os

from werkzeug.serving import run_simple

os.environ.setdefault("DATABASE_URL", "postgresql://postgres:123@localhost:5432/garage_manager")
os.environ.setdefault("SKIP_REDIS", "1")
os.environ["FLASK_RUN_FROM_CLI"] = "false"

from app import application

run_simple("127.0.0.1", 5000, application, use_reloader=False, use_debugger=False)
