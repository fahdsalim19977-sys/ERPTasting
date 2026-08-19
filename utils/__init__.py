# utils/__init__.py
from .helpers import (
    log_activity,
    check_role,
    get_company_settings,
    get_trainers,
    get_lang,
    t
)
from .decorators import login_required, role_required, permission_required