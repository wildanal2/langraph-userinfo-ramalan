import re
from datetime import datetime
from typing import Optional

def sanitize_input(text: str, max_length: int = 500) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    text = text.strip()[:max_length]
    return text

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate Indonesian phone number"""
    cleaned = phone.replace('-', '').replace(' ', '').replace('+', '')
    pattern = r'^(62|0)[0-9]{9,12}$'
    return bool(re.match(pattern, cleaned))

def validate_date(date_str: str) -> bool:
    """Validate date format (DD-MM-YYYY, DD/MM/YYYY, or YYYY-MM-DD)"""
    formats = ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d %B %Y', '%d %b %Y']
    for fmt in formats:
        try:
            date_obj = datetime.strptime(date_str.strip(), fmt)
            if 1900 <= date_obj.year <= datetime.now().year:
                return True
        except ValueError:
            continue
    return False
