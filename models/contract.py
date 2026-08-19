# models/contract.py
from .base import get_db
from datetime import datetime

class ContractType:
    """نموذج نوع العقد"""
    
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.description = data.get('description')
        self.is_active = data.get('is_active', 1)
        self.created_at = data['created_at']
    
    @staticmethod
    def get_all():
        conn = get_db()
        types = conn.execute('SELECT * FROM contract_types ORDER BY name').fetchall()
        conn.close()
        return [ContractType(t) for t in types]

class Contract:
    """نموذج العقد"""
    
    def __init__(self, contract_data):
        self.id = contract_data['id']
        self.client_id = contract_data['client_id']
        self.contract_type_id = contract_data.get('contract_type_id')
        self.contract_number = contract_data['contract_number']
        self.title = contract_data['title']
        self.description = contract_data.get('description')
        self.start_date = contract_data['start_date']
        self.end_date = contract_data['end_date']
        self.contract_value = contract_data.get('contract_value', 0)
        self.total_amount = contract_data.get('total_amount', 0)
        self.paid_amount = contract_data.get('paid_amount', 0)
        self.payment_status = contract_data.get('payment_status', 'غير مدفوع')
        self.status = contract_data.get('status', 'نشط')
        self.file_path = contract_data.get('file_path')
        self.notes = contract_data.get('notes')
        self.created_by = contract_data['created_by']
        self.created_at = contract_data['created_at']
        self.updated_at = contract_data.get('updated_at')
    
    @staticmethod
    def get_by_id(contract_id):
        conn = get_db()
        contract = conn.execute('SELECT * FROM client_contracts WHERE id = ?', (contract_id,)).fetchone()
        conn.close()
        if contract:
            return Contract(contract)
        return None
    
    @staticmethod
    def get_by_client(client_id):
        conn = get_db()
        contracts = conn.execute('''
            SELECT * FROM client_contracts WHERE client_id = ? ORDER BY created_at DESC
        ''', (client_id,)).fetchall()
        conn.close()
        return [Contract(c) for c in contracts]
    
    @staticmethod
    def get_all():
        conn = get_db()
        contracts = conn.execute('SELECT * FROM client_contracts ORDER BY created_at DESC').fetchall()
        conn.close()
        return [Contract(c) for c in contracts]
    
    @staticmethod
    def create(client_id, contract_number, title, start_date, end_date, created_by,
               contract_type_id=None, description=None, contract_value=0, 
               total_amount=0, status='نشط', notes=None):
        conn = get_db()
        cursor = conn.execute('''
            INSERT INTO client_contracts 
            (client_id, contract_type_id, contract_number, title, description, 
             start_date, end_date, contract_value, total_amount, status, notes, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (client_id, contract_type_id, contract_number, title, description, 
              start_date, end_date, contract_value, total_amount, status, notes, created_by))
        contract_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return contract_id
    
    def get_payments(self):
        conn = get_db()
        payments = conn.execute('''
            SELECT * FROM contract_payments WHERE contract_id = ? ORDER BY installment_number ASC
        ''', (self.id,)).fetchall()
        conn.close()
        return [ContractPayment(p) for p in payments]
    
    def get_attachments(self):
        conn = get_db()
        attachments = conn.execute('''
            SELECT ca.*, u.name as uploaded_by_name
            FROM contract_attachments ca
            JOIN users u ON ca.uploaded_by = u.id
            WHERE ca.contract_id = ?
            ORDER BY ca.created_at DESC
        ''', (self.id,)).fetchall()
        conn.close()
        return [ContractAttachment(a) for a in attachments]

class ContractPayment:
    """نموذج دفعة العقد"""
    
    def __init__(self, data):
        self.id = data['id']
        self.contract_id = data['contract_id']
        self.installment_number = data['installment_number']
        self.amount = data['amount']
        self.paid_amount = data.get('paid_amount', 0)
        self.due_date = data['due_date']
        self.payment_date = data.get('payment_date')
        self.status = data.get('status', 'مستحقة')
        self.notes = data.get('notes')
        self.created_at = data['created_at']
        self.updated_at = data.get('updated_at')
    
    def mark_paid(self, paid_amount, payment_date=None):
        if not payment_date:
            payment_date = datetime.now().strftime('%Y-%m-%d')
        
        new_paid_amount = (self.paid_amount or 0) + paid_amount
        
        if new_paid_amount >= self.amount:
            status = 'مدفوعة'
        else:
            status = 'مدفوعة جزئيا'
        
        conn = get_db()
        conn.execute('''
            UPDATE contract_payments 
            SET paid_amount = ?, status = ?, payment_date = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_paid_amount, status, payment_date, self.id))
        conn.commit()
        conn.close()
        
        self._update_contract_status()
    
    def _update_contract_status(self):
        conn = get_db()
        
        total_paid = conn.execute('''
            SELECT SUM(paid_amount) as total FROM contract_payments WHERE contract_id = ?
        ''', (self.contract_id,)).fetchone()['total'] or 0
        
        contract = conn.execute('SELECT total_amount, contract_value FROM client_contracts WHERE id = ?', 
                               (self.contract_id,)).fetchone()
        total = contract['total_amount'] or contract['contract_value'] or 0
        
        if total == 0:
            payment_status = 'غير مدفوع'
        elif total_paid >= total:
            payment_status = 'مدفوع بالكامل'
        elif total_paid > 0:
            payment_status = 'مدفوع جزئيا'
        else:
            payment_status = 'غير مدفوع'
        
        conn.execute('''
            UPDATE client_contracts 
            SET paid_amount = ?, payment_status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (total_paid, payment_status, self.contract_id))
        conn.commit()
        conn.close()

class ContractAttachment:
    """نموذج مرفق العقد"""
    
    def __init__(self, data):
        self.id = data['id']
        self.contract_id = data['contract_id']
        self.file_name = data['file_name']
        self.file_path = data['file_path']
        self.file_size = data.get('file_size', 0)
        self.file_type = data.get('file_type')
        self.uploaded_by = data['uploaded_by']
        self.uploaded_by_name = data.get('uploaded_by_name')
        self.description = data.get('description')
        self.created_at = data['created_at']

def create_tables():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contract_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
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
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contract_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER NOT NULL,
            installment_number INTEGER NOT NULL,
            amount REAL NOT NULL,
            paid_amount REAL DEFAULT 0,
            due_date DATE NOT NULL,
            payment_date DATE,
            status TEXT CHECK(status IN ('مستحقة', 'مدفوعة', 'مدفوعة جزئيا', 'متأخرة')) DEFAULT 'مستحقة',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contract_attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER DEFAULT 0,
            file_type TEXT,
            uploaded_by INTEGER NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("SELECT COUNT(*) as count FROM contract_types")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO contract_types (name, description)
            VALUES 
            ('عقد خدمات', 'عقد تقديم خدمات استشارية أو تقنية'),
            ('عقد مقاولات', 'عقد أعمال مقاولات وإنشاءات'),
            ('عقد توريد', 'عقد توريد مواد أو معدات'),
            ('عقد تدريب', 'عقد تقديم دورات تدريبية')
        """)
    
    conn.commit()
    conn.close()
    print("✅ تم تهيئة جداول العقود")