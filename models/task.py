# models/task.py
from .base import get_db
from datetime import datetime

class Task:
    """نموذج المهمة/التدريب"""
    
    def __init__(self, task_data):
        self.id = task_data['id']
        self.client_id = task_data['client_id']
        self.created_by = task_data.get('created_by')
        self.assigned_user_id = task_data.get('assigned_user_id')
        self.trainer_id = task_data.get('trainer_id')
        self.title = task_data['title']
        self.description = task_data.get('description')
        self.status = task_data.get('status', 'لم تبدأ')
        self.priority = task_data.get('priority', 'متوسطة')
        self.due_date = task_data['due_date']
        self.completion_percentage = task_data.get('completion_percentage', 0)
        self.task_group = task_data.get('task_group')
        self.meeting_id = task_data.get('meeting_id')
        self.estimated_duration = task_data.get('estimated_duration', 0)
        self.actual_duration = task_data.get('actual_duration', 0)
        self.contract_payment_id = task_data.get('contract_payment_id')
        self.created_at = task_data['created_at']
        self.updated_at = task_data.get('updated_at')
    
    @staticmethod
    def get_by_id(task_id):
        conn = get_db()
        task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
        conn.close()
        if task:
            return Task(task)
        return None
    
    @staticmethod
    def get_by_client(client_id):
        conn = get_db()
        tasks = conn.execute('''
            SELECT * FROM tasks WHERE client_id = ? ORDER BY due_date ASC
        ''', (client_id,)).fetchall()
        conn.close()
        return [Task(task) for task in tasks]
    
    @staticmethod
    def get_all():
        conn = get_db()
        tasks = conn.execute('SELECT * FROM tasks ORDER BY due_date ASC').fetchall()
        conn.close()
        return [Task(task) for task in tasks]
    
    @staticmethod
    def create(client_id, title, due_date, created_by, assigned_user_id=None, 
               trainer_id=None, description=None, priority='متوسطة', 
               estimated_duration=0, meeting_id=None, task_group=None, 
               contract_payment_id=None):
        conn = get_db()
        cursor = conn.execute('''
            INSERT INTO tasks (client_id, created_by, assigned_user_id, trainer_id, 
                             title, description, due_date, priority, 
                             estimated_duration, meeting_id, task_group, 
                             contract_payment_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (client_id, created_by, assigned_user_id, trainer_id, 
              title, description, due_date, priority, 
              estimated_duration, meeting_id, task_group, 
              contract_payment_id))
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id
    
    def update(self, **kwargs):
        conn = get_db()
        set_clause = []
        values = []
        for key, value in kwargs.items():
            if key in ['client_id', 'assigned_user_id', 'trainer_id', 'title', 
                      'description', 'due_date', 'priority', 'estimated_duration', 
                      'task_group', 'contract_payment_id', 'status', 
                      'completion_percentage', 'actual_duration']:
                set_clause.append(f"{key} = ?")
                values.append(value)
        
        if set_clause:
            values.append(self.id)
            query = f"UPDATE tasks SET {', '.join(set_clause)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            conn.execute(query, values)
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False
    
    def delete(self):
        conn = get_db()
        conn.execute('DELETE FROM tasks WHERE id = ?', (self.id,))
        conn.commit()
        conn.close()
    
    def get_updates(self):
        conn = get_db()
        updates = conn.execute('''
            SELECT tu.*, u.name as user_name
            FROM task_updates tu
            JOIN users u ON tu.user_id = u.id
            WHERE tu.task_id = ?
            ORDER BY tu.created_at DESC
        ''', (self.id,)).fetchall()
        conn.close()
        return [TaskUpdate(update) for update in updates]
    
    def add_update(self, user_id, note, attachment_path=None):
        conn = get_db()
        conn.execute('''
            INSERT INTO task_updates (task_id, user_id, note, attachment_path)
            VALUES (?, ?, ?, ?)
        ''', (self.id, user_id, note, attachment_path))
        conn.commit()
        conn.close()

class TaskUpdate:
    """نموذج تحديث المهمة"""
    
    def __init__(self, data):
        self.id = data['id']
        self.task_id = data['task_id']
        self.user_id = data['user_id']
        self.user_name = data.get('user_name')
        self.note = data.get('note')
        self.attachment_path = data.get('attachment_path')
        self.created_at = data['created_at']

def create_tables():
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
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            note TEXT,
            attachment_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ تم تهيئة جداول المهام")