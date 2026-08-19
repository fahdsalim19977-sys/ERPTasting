# models/trainer.py
from .base import get_db

class Trainer:
    """نموذج المدرب"""
    
    def __init__(self, trainer_data):
        self.id = trainer_data['id']
        self.name = trainer_data['name']
        self.phone = trainer_data.get('phone')
        self.email = trainer_data.get('email')
        self.specialty = trainer_data.get('specialty')
        self.notes = trainer_data.get('notes')
        self.is_active = trainer_data.get('is_active', 1)
        self.created_at = trainer_data['created_at']
    
    @staticmethod
    def get_by_id(trainer_id):
        conn = get_db()
        trainer = conn.execute('SELECT * FROM trainers WHERE id = ?', (trainer_id,)).fetchone()
        conn.close()
        if trainer:
            return Trainer(trainer)
        return None
    
    @staticmethod
    def get_all():
        conn = get_db()
        trainers = conn.execute('SELECT * FROM trainers ORDER BY name').fetchall()
        conn.close()
        return [Trainer(trainer) for trainer in trainers]

def create_tables():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trainers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            specialty TEXT,
            notes TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ تم تهيئة جداول المدربين")