# models/client.py
from .base import get_db
from .user import User
from .trainer import Trainer

class Client:
    """نموذج العميل"""
    
    def __init__(self, client_data):
        self.id = client_data['id']
        self.name = client_data['name']
        self.phone = client_data.get('phone')
        self.email = client_data.get('email')
        self.address = client_data.get('address')
        self.company_name = client_data.get('company_name')
        self.notes = client_data.get('notes')
        self.created_at = client_data['created_at']
    
    @staticmethod
    def get_by_id(client_id):
        """جلب عميل حسب ID"""
        conn = get_db()
        client = conn.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()
        conn.close()
        if client:
            return Client(client)
        return None
    
    @staticmethod
    def get_all():
        """جلب جميع العملاء"""
        conn = get_db()
        clients = conn.execute('SELECT * FROM clients ORDER BY name').fetchall()
        conn.close()
        return [Client(client) for client in clients]
    
    @staticmethod
    def create(name, phone=None, email=None, address=None, company_name=None, notes=None):
        """إنشاء عميل جديد"""
        conn = get_db()
        cursor = conn.execute('''
            INSERT INTO clients (name, phone, email, address, company_name, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, phone, email, address, company_name, notes))
        client_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return client_id
    
    def update(self, name, phone=None, email=None, address=None, company_name=None, notes=None):
        """تحديث بيانات العميل"""
        conn = get_db()
        conn.execute('''
            UPDATE clients SET 
                name = ?, phone = ?, email = ?, address = ?, 
                company_name = ?, notes = ?
            WHERE id = ?
        ''', (name, phone, email, address, company_name, notes, self.id))
        conn.commit()
        conn.close()
    
    def delete(self):
        """حذف العميل"""
        conn = get_db()
        conn.execute('DELETE FROM clients WHERE id = ?', (self.id,))
        conn.commit()
        conn.close()
    
    def get_trainers(self):
        """جلب المدربين المرتبطين بالعميل"""
        conn = get_db()
        trainers = conn.execute('''
            SELECT t.* FROM trainers t
            JOIN client_trainers ct ON t.id = ct.trainer_id
            WHERE ct.client_id = ?
        ''', (self.id,)).fetchall()
        conn.close()
        return [Trainer(trainer) for trainer in trainers]
    
    def add_trainer(self, trainer_id):
        """ربط مدرب بالعميل"""
        conn = get_db()
        conn.execute('''
            INSERT OR IGNORE INTO client_trainers (client_id, trainer_id)
            VALUES (?, ?)
        ''', (self.id, trainer_id))
        conn.commit()
        conn.close()
    
    def remove_trainer(self, trainer_id):
        """إزالة مدرب من العميل"""
        conn = get_db()
        conn.execute('''
            DELETE FROM client_trainers WHERE client_id = ? AND trainer_id = ?
        ''', (self.id, trainer_id))
        conn.commit()
        conn.close()

class ClientTrainer:
    """نموذج ربط العميل بالمدرب"""
    
    def __init__(self, data):
        self.id = data['id']
        self.client_id = data['client_id']
        self.trainer_id = data['trainer_id']

def create_tables():
    """إنشاء جداول العملاء"""
    conn = get_db()
    cursor = conn.cursor()
    
    # ===== جدول العملاء =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            company_name TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # ===== جدول ربط العملاء بالمدربين =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS client_trainers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            trainer_id INTEGER NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
            FOREIGN KEY (trainer_id) REFERENCES trainers(id) ON DELETE CASCADE,
            UNIQUE(client_id, trainer_id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ تم تهيئة جداول العملاء")