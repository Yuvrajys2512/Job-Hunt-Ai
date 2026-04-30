# Resume model is defined in application.py (co-located with Application)
# This file exists so `from app.models import resume` works in init_db()
from app.models.application import Resume  # noqa: F401
