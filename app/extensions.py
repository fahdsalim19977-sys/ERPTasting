# app/extensions.py
from flask_wtf.csrf import CSRFProtect

# ===== إضافات Flask =====
csrf = CSRFProtect()

def init_extensions(app):
    """تهيئة جميع الإضافات"""
    csrf.init_app(app)