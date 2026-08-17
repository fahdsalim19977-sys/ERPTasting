# models/base.py
import os
import sqlite3
from datetime import datetime

# ===== مسار قاعدة البيانات =====
# استخدام مسار افتراضي إذا لم يكن معرفاً
DB_PATH = os.environ.get('DATABASE_URL') or '/app/data/tasks.db'

# إذا كان المسار فارغاً، استخدم المسار الافتراضي
if not DB_PATH:
    DB_PATH = '/app/data/tasks.db'

# ===== لو على جهاز محلي =====
if not os.path.exists('/app/data'):
    DB_PATH = 'tasks.db'

def get_db():
    """الحصول على اتصال بقاعدة البيانات"""
    # التأكد من وجود المجلد
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA cache_size=10000')
    conn.execute('PRAGMA busy_timeout=30000')
    return conn

def init_db():
    """تهيئة قاعدة البيانات - إنشاء جميع الجداول"""
    from .user import create_tables as create_user_tables
    from .client import create_tables as create_client_tables
    from .trainer import create_tables as create_trainer_tables
    from .task import create_tables as create_task_tables
    from .contract import create_tables as create_contract_tables
    from .payment import create_tables as create_payment_tables
    
    print("🚀 جاري تهيئة قاعدة البيانات...")
    
    create_user_tables()
    create_client_tables()
    create_trainer_tables()
    create_task_tables()
    create_contract_tables()
    create_payment_tables()
    
    print(f"✅ تم تهيئة قاعدة البيانات في: {DB_PATH}")