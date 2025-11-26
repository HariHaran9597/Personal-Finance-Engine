# src/config.py
import os

# File Paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
RAW_DATA_PATH = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_PATH = os.path.join(DATA_DIR, 'processed')

# Data Schema
REQUIRED_COLUMNS = ['date', 'description', 'amount', 'type']
DATE_FORMAT = '%Y-%m-%d'

# Transaction Categories (Classes for ML)
CATEGORIES = [
    'Food & Dining',
    'Transportation',
    'Shopping',
    'Bills & Utilities',
    'Entertainment',
    'Health & Wellness',
    'Income',
    'Transfer',
    'Other'
]