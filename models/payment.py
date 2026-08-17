# models/payment.py
from .base import get_db

def create_tables():
    """إنشاء جداول المدفوعات"""
    conn = get_db()
    cursor = conn.cursor()
    
    # ===== جدول المدفوعات =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS client_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            module_id INTEGER,
            amount REAL NOT NULL,
            payment_date DATE NOT NULL,
            due_date DATE,
            payment_method TEXT CHECK(payment_method IN ('نقدي', 'تحويل بنكي', 'شيك', 'بطاقة ائتمان', 'أخرى')) DEFAULT 'نقدي',
            status TEXT CHECK(status IN ('مدفوع', 'معلق', 'متأخر')) DEFAULT 'معلق',
            invoice_number TEXT,
            notes TEXT,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ تم تهيئة جداول المدفوعات")