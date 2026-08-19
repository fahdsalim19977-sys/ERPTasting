# models/payment.py
from .base import get_db
from datetime import datetime

class Payment:
    """نموذج الدفعة"""
    
    def __init__(self, payment_data):
        self.id = payment_data['id']
        self.client_id = payment_data['client_id']
        self.module_id = payment_data.get('module_id')
        self.amount = payment_data['amount']
        self.payment_date = payment_data['payment_date']
        self.due_date = payment_data.get('due_date')
        self.payment_method = payment_data.get('payment_method', 'نقدي')
        self.status = payment_data.get('status', 'معلق')
        self.invoice_number = payment_data.get('invoice_number')
        self.notes = payment_data.get('notes')
        self.created_by = payment_data['created_by']
        self.created_at = payment_data['created_at']
    
    @staticmethod
    def get_by_id(payment_id):
        """جلب دفعة حسب ID"""
        conn = get_db()
        payment = conn.execute('SELECT * FROM client_payments WHERE id = ?', (payment_id,)).fetchone()
        conn.close()
        if payment:
            return Payment(payment)
        return None
    
    @staticmethod
    def get_by_client(client_id):
        """جلب دفعات عميل معين"""
        conn = get_db()
        payments = conn.execute('''
            SELECT * FROM client_payments WHERE client_id = ? ORDER BY created_at DESC
        ''', (client_id,)).fetchall()
        conn.close()
        return [Payment(p) for p in payments]
    
    @staticmethod
    def get_all():
        """جلب جميع الدفعات"""
        conn = get_db()
        payments = conn.execute('SELECT * FROM client_payments ORDER BY created_at DESC').fetchall()
        conn.close()
        return [Payment(p) for p in payments]
    
    @staticmethod
    def create(client_id, amount, payment_date, created_by, module_id=None,
               due_date=None, payment_method='نقدي', status='معلق',
               invoice_number=None, notes=None):
        """إنشاء دفعة جديدة"""
        conn = get_db()
        cursor = conn.execute('''
            INSERT INTO client_payments 
            (client_id, module_id, amount, payment_date, due_date, 
             payment_method, status, invoice_number, notes, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (client_id, module_id, amount, payment_date, due_date, 
              payment_method, status, invoice_number, notes, created_by))
        payment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return payment_id
    
    def update(self, **kwargs):
        """تحديث بيانات الدفعة"""
        conn = get_db()
        set_clause = []
        values = []
        for key, value in kwargs.items():
            if key in ['amount', 'payment_date', 'due_date', 'payment_method', 
                      'status', 'invoice_number', 'notes']:
                set_clause.append(f"{key} = ?")
                values.append(value)
        
        if set_clause:
            values.append(self.id)
            query = f"UPDATE client_payments SET {', '.join(set_clause)} WHERE id = ?"
            conn.execute(query, values)
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False
    
    def delete(self):
        """حذف الدفعة"""
        conn = get_db()
        conn.execute('DELETE FROM client_payments WHERE id = ?', (self.id,))
        conn.commit()
        conn.close()

class PaymentInstallment:
    """نموذج دفعة مقسطة"""
    
    def __init__(self, data):
        self.id = data['id']
        self.payment_id = data['payment_id']
        self.installment_number = data['installment_number']
        self.amount = data['amount']
        self.due_date = data['due_date']
        self.status = data.get('status', 'مستحق')
        self.paid_date = data.get('paid_date')
        self.notes = data.get('notes')

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
    
    # ===== جدول الدفعات المقسمة =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_installments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_id INTEGER NOT NULL,
            installment_number INTEGER NOT NULL,
            amount REAL NOT NULL,
            due_date DATE NOT NULL,
            status TEXT CHECK(status IN ('مستحق', 'مدفوع', 'متأخر')) DEFAULT 'مستحق',
            paid_date DATE,
            notes TEXT,
            FOREIGN KEY (payment_id) REFERENCES client_payments(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ تم تهيئة جداول المدفوعات")