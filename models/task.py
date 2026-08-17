# models/task.py
from .base import get_db

def create_tables():
    """إنشاء جداول المهام"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            created_by INTEGER,
            assigned_user_id INTEGER,
            trainer_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT CHECK(status IN ('لم تبدأ', 'قيد التنفيذ', 'مراجعة', 'مكتملة', 'متأخرة')) DEFAULT 'لم تبدأ',
            priority TEXT CHECK(priority IN ('منخفضة', 'متوسطة', 'عالية')) DEFAULT 'متوسطة',
            due_date DATE NOT NULL,
            completion_percentage INTEGER DEFAULT 0,
            task_group TEXT,
            meeting_id INTEGER,
            estimated_duration INTEGER DEFAULT 0,
            actual_duration INTEGER DEFAULT 0,
            contract_payment_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ تم تهيئة جداول المهام")