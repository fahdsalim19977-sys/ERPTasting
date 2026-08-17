# models/__init__.py
from .base import get_db, init_db
from .user import User, hash_password, verify_password
from .client import Client, ClientTrainer
from .trainer import Trainer
from .task import Task, TaskUpdate
from .contract import Contract, ContractPayment, ContractAttachment, ContractType
from .payment import Payment, PaymentInstallment

__all__ = [
    'get_db', 'init_db',
    'User', 'hash_password', 'verify_password',
    'Client', 'ClientTrainer',
    'Trainer',
    'Task', 'TaskUpdate',
    'Contract', 'ContractPayment', 'ContractAttachment', 'ContractType',
    'Payment', 'PaymentInstallment'
]