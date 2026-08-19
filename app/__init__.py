# app/__init__.py
from flask import Flask
from app.config import Config
from app.extensions import init_extensions
import os

def create_app(config_class=Config):
    """مصنع تطبيق Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # ===== المفتاح السري =====
    app.secret_key = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # ===== إنشاء المجلدات =====
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'contracts'), exist_ok=True)
    
    # ===== تهيئة الإضافات =====
    init_extensions(app)
    
    # ===== تهيئة قاعدة البيانات =====
    from models import init_db
    init_db()
    
    # ===== تسجيل الـ Blueprints =====
    register_blueprints(app)
    
    # ===== دوال السياق =====
    register_context_processors(app)
    
    # ===== معالج الأخطاء =====
    register_error_handlers(app)
    
    return app

def register_blueprints(app):
    """تسجيل جميع الـ Blueprints"""
    from app.routes import (
        auth_bp, users_bp, clients_bp, trainers_bp, tasks_bp,
        contracts_bp, payments_bp, modules_bp, meetings_bp,
        reports_bp, settings_bp, backups_bp
    )
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(trainers_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(contracts_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(modules_bp)
    app.register_blueprint(meetings_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(backups_bp)

def register_context_processors(app):
    """تسجيل دوال السياق"""
    from utils import get_company_settings, get_lang, t
    from datetime import datetime
    
    @app.context_processor
    def utility_processor():
        settings = get_company_settings()
        return {
            't': t,
            'get_lang': get_lang,
            'datetime': datetime,
            'settings': settings
        }

def register_error_handlers(app):
    """تسجيل معالج الأخطاء"""
    from flask import render_template
    from utils import get_company_settings
    
    @app.errorhandler(404)
    def page_not_found(e):
        settings = get_company_settings()
        return render_template('404.html', settings=settings), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        from flask import flash, redirect, url_for
        flash('❌ حدث خطأ في السيرفر. يرجى المحاولة مرة أخرى.', 'danger')
        return redirect(url_for('index'))
    