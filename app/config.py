# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """إعدادات التطبيق الأساسية"""
    
    # ===== الأمان =====
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # ===== قاعدة البيانات =====
    DB_PATH = os.environ.get('DATABASE_URL') or '/app/data/tasks.db'
    
    # ===== المجلدات =====
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads/'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # ===== البريد =====
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or ''
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or ''

class DevelopmentConfig(Config):
    """إعدادات بيئة التطوير"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """إعدادات بيئة الاختبار"""
    DEBUG = False
    TESTING = True
    DB_PATH = 'test.db'

class ProductionConfig(Config):
    """إعدادات بيئة الإنتاج"""
    DEBUG = False
    TESTING = False