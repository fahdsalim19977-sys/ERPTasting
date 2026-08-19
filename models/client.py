# models/client.py
from .base import get_db

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
        conn = get_db()
        client = conn.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()
        conn.close()
        if client:
            return Client(client)
        return None
    
    @staticmethod
    def get_all():
        conn = get_db()
        clients = conn.execute('SELECT * FROM clients ORDER BY name').fetchall()
        conn.close()
        return [Client(client) for client in clients]
    
    @staticmethod
    def create(name, phone=None, email=None, address=None, company_name=None, notes=None):
        conn = get_db()
        cursor = conn.execute('''
            INSERT INTO clients (name, phone, email, address, company_name, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, phone, email, address, company_name, notes))
        client_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return client_id

class ClientTrainer:
    """نموذج ربط العميل بالمدرب"""
    
    def __init__(self, data):
        self.id = data['id']
        self.client_id = data['client_id']
        self.trainer_id = data['trainer_id']

def create_tables():
    conn = get_db()
    cursor = conn.cursor()
    
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