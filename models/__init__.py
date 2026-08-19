# models/__init__.py
from .base import get_db, init_db
from .user import User, hash_password, verify_password
from .client import Client, ClientTrainer
from .trainer import Trainer
from .task import Task, TaskUpdate
from .contract import Contract, ContractPayment, ContractAttachment, ContractType
from .payment import Payment, PaymentInstallment

# ===== دوال الصلاحيات =====
def get_user_permissions(user_id):
    """جلب جميع صلاحيات المستخدم (من دوره + صلاحياته الخاصة)"""
    conn = get_db()
    cursor = conn.cursor()
    
    # صلاحيات من الدور
    cursor.execute("""
        SELECT DISTINCT p.name
        FROM permissions p
        JOIN role_permissions rp ON p.id = rp.permission_id
        JOIN users u ON u.id = ?
        WHERE u.id = ?
    """, (user_id, user_id))
    
    permissions = {row[0] for row in cursor.fetchall()}
    
    # صلاحيات إضافية من user_permissions
    cursor.execute("""
        SELECT p.name
        FROM permissions p
        JOIN user_permissions up ON p.id = up.permission_id
        WHERE up.user_id = ?
    """, (user_id,))
    
    for row in cursor.fetchall():
        permissions.add(row[0])
    
    conn.close()
    return permissions

def has_permission(user_id, permission_name):
    """التحقق من وجود صلاحية معينة للمستخدم"""
    permissions = get_user_permissions(user_id)
    return permission_name in permissions

def add_permission_to_user(user_id, permission_name):
    """إضافة صلاحية معينة للمستخدم"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM permissions WHERE name = ?", (permission_name,))
    perm = cursor.fetchone()
    if perm:
        cursor.execute("""
            INSERT OR IGNORE INTO user_permissions (user_id, permission_id)
            VALUES (?, ?)
        """, (user_id, perm[0]))
        conn.commit()
    
    conn.close()

def remove_permission_from_user(user_id, permission_name):
    """إزالة صلاحية معينة من المستخدم"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM permissions WHERE name = ?", (permission_name,))
    perm = cursor.fetchone()
    if perm:
        cursor.execute("""
            DELETE FROM user_permissions
            WHERE user_id = ? AND permission_id = ?
        """, (user_id, perm[0]))
        conn.commit()
    
    conn.close()

__all__ = [
    'get_db', 'init_db',
    'User', 'hash_password', 'verify_password',
    'Client', 'ClientTrainer',
    'Trainer',
    'Task', 'TaskUpdate',
    'Contract', 'ContractPayment', 'ContractAttachment', 'ContractType',
    'Payment', 'PaymentInstallment',
    'get_user_permissions', 'has_permission',
    'add_permission_to_user', 'remove_permission_from_user'
]