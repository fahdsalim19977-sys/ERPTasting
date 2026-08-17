# models/contract.py
from .base import get_db

def create_tables():
    """إنشاء جداول العقود"""
    conn = get_db()
    cursor = conn.cursor()
    
    # ===== جدول العقود =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS client_contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            contract_type_id INTEGER,
            contract_number TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            contract_value REAL DEFAULT 0,
            total_amount REAL DEFAULT 0,
            paid_amount REAL DEFAULT 0,
            payment_status TEXT CHECK(payment_status IN ('غير مدفوع', 'مدفوع جزئيا', 'مدفوع بالكامل')) DEFAULT 'غير مدفوع',
            status TEXT CHECK(status IN ('نشط', 'منتهي', 'ملغي', 'معلق')) DEFAULT 'نشط',
            file_path TEXT,
            notes TEXT,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ تم تهيئة جداول العقود")