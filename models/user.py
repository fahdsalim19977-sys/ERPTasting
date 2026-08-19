# models/user.py
from .base import get_db
import hashlib
import bcrypt

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

class User:
    """نموذج المستخدم"""
    
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.name = user_data['name']
        self.email = user_data['email']
        self.password = user_data['password']
        self.role = user_data['role']
        self.is_active = user_data['is_active']
        self.created_at = user_data['created_at']
    
    @staticmethod
    def get_by_id(user_id):
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if user:
            return User(user)
        return None
    
    @staticmethod
    def get_by_username(username):
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user:
            return User(user)
        return None
    
    @staticmethod
    def get_all():
        conn = get_db()
        users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
        conn.close()
        return [User(user) for user in users]
    
    @staticmethod
    def create(username, name, email, password, role):
        conn = get_db()
        try:
            conn.execute('''
                INSERT INTO users (username, name, email, password, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, name, email, hash_password(password), role))
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()

def create_tables():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT CHECK(role IN ('مدير', 'موظف', 'مراقب')) NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            resource TEXT NOT NULL,
            action TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            is_default INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS role_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id INTEGER NOT NULL,
            permission_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
            FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
            UNIQUE(role_id, permission_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            permission_id INTEGER NOT NULL,
            granted_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
            FOREIGN KEY (granted_by) REFERENCES users(id),
            UNIQUE(user_id, permission_id)
        )
    """)
    
    # ===== الصلاحيات الافتراضية =====
    default_permissions = [
        ('tasks.view', 'tasks', 'view', 'عرض المهام'),
        ('tasks.create', 'tasks', 'create', 'إنشاء مهام'),
        ('tasks.edit', 'tasks', 'edit', 'تعديل المهام'),
        ('tasks.delete', 'tasks', 'delete', 'حذف المهام'),
        ('tasks.assign', 'tasks', 'assign', 'تعيين المهام'),
        ('clients.view', 'clients', 'view', 'عرض العملاء'),
        ('clients.create', 'clients', 'create', 'إنشاء عملاء'),
        ('clients.edit', 'clients', 'edit', 'تعديل العملاء'),
        ('clients.delete', 'clients', 'delete', 'حذف العملاء'),
        ('contracts.view', 'contracts', 'view', 'عرض العقود'),
        ('contracts.create', 'contracts', 'create', 'إنشاء عقود'),
        ('contracts.edit', 'contracts', 'edit', 'تعديل العقود'),
        ('payments.view', 'payments', 'view', 'عرض المدفوعات'),
        ('payments.create', 'payments', 'create', 'إنشاء مدفوعات'),
        ('payments.edit', 'payments', 'edit', 'تعديل المدفوعات'),
        ('reports.view', 'reports', 'view', 'عرض التقارير'),
        ('reports.export', 'reports', 'export', 'تصدير التقارير'),
        ('users.view', 'users', 'view', 'عرض المستخدمين'),
        ('users.create', 'users', 'create', 'إنشاء مستخدمين'),
        ('users.edit', 'users', 'edit', 'تعديل المستخدمين'),
        ('users.delete', 'users', 'delete', 'حذف المستخدمين'),
    ]
    
    for perm_name, resource, action, description in default_permissions:
        cursor.execute("""
            INSERT OR IGNORE INTO permissions (name, resource, action, description)
            VALUES (?, ?, ?, ?)
        """, (perm_name, resource, action, description))
    
    # ===== الأدوار الافتراضية =====
    default_roles = [
        ('مدير', 'مدير النظام - لديه جميع الصلاحيات', 0),
        ('موظف', 'موظف عادي - صلاحيات محدودة', 1),
        ('مراقب', 'مشاهد - صلاحيات عرض فقط', 0),
    ]
    
    for role_name, description, is_default in default_roles:
        cursor.execute("""
            INSERT OR IGNORE INTO roles (name, description, is_default)
            VALUES (?, ?, ?)
        """, (role_name, description, is_default))
    
    # ===== المستخدمين الافتراضيين =====
    cursor.execute("SELECT * FROM users WHERE username = 'Adminerp'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (username, name, email, password, role)
            VALUES (?, ?, ?, ?, ?)
        """, ('Adminerp', 'مدير النظام', 'adminerp@company.com', hash_password('1234'), 'مدير'))
    
    cursor.execute("SELECT * FROM users WHERE username = 'Fahd01'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (username, name, email, password, role)
            VALUES (?, ?, ?, ?, ?)
        """, ('Fahd01', 'فهد المدير', 'fahd@company.com', hash_password('1234'), 'مدير'))
    
    cursor.execute("SELECT * FROM users WHERE username = 'employee1'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (username, name, email, password, role)
            VALUES 
            ('employee1', 'سارة موظف', 'sara@company.com', ?, 'موظف'),
            ('viewer1', 'خالد مراقب', 'khalid@company.com', ?, 'مراقب')
        """, (hash_password('1234'), hash_password('1234')))
    
    # ===== ربط الأدوار بالصلاحيات =====
    roles_map = {}
    cursor.execute("SELECT id, name FROM roles")
    for row in cursor.fetchall():
        roles_map[row[1]] = row[0]
    
    perms_map = {}
    cursor.execute("SELECT id, name FROM permissions")
    for row in cursor.fetchall():
        perms_map[row[1]] = row[0]
    
    if 'مدير' in roles_map:
        for perm_id in perms_map.values():
            cursor.execute("""
                INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                VALUES (?, ?)
            """, (roles_map['مدير'], perm_id))
    
    conn.commit()
    conn.close()
    print("✅ تم تهيئة جداول المستخدمين والصلاحيات")