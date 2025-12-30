import pytest
from src.core.security import sanitize_input, validate_email, validate_phone

def test_sanitize_input():
    assert sanitize_input("  hello  ") == "hello"
    assert sanitize_input("a" * 600, max_length=500) == "a" * 500
    assert sanitize_input("") == ""

def test_validate_email():
    assert validate_email("test@example.com") == True
    assert validate_email("invalid-email") == False
    assert validate_email("test@") == False

def test_validate_phone():
    assert validate_phone("081234567890") == True
    assert validate_phone("+6281234567890") == True
    assert validate_phone("1234") == False
