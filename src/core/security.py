import re
from datetime import datetime
from typing import Tuple, Optional
from src.core.indonesia_locations import INDONESIA_CITIES_AND_REGENCIES

def sanitize_input(text: str, max_length: int = 500) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    text = text.strip()[:max_length]
    return text


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format and check for typos.
    Returns (is_valid: bool, error_code: str | None)
    error_code can be 'invalid_format' or 'typo_detected'
    """
    # 1. Validate Format
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "invalid_format"

    # 2. Check for Typos
    common_domains = {
        "gmail.com": ["gmil.com", "gmal.com", "gmali.com", "gmaill.com", "gmai.com", "gmail.co", "ymail.com"],
        "yahoo.com": ["yaho.com", "yahoo.co", "yhoo.com", "yahoo.co.id"],
        "hotmail.com": ["hotmil.com", "hotmal.com", "hotmail.co"],
        "outlook.com": ["outlok.com", "outlook.co"],
        "icloud.com": ["iclud.com", "icloud.co"]
    }
    
    try:
        domain = email.split("@")[1]
    except IndexError:
        return False, "invalid_format"
    
    for correct, typos in common_domains.items():
        if domain in typos:
            return False, "typo_detected"
            
    return True, None


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Validate and format Indonesian phone number.
    Returns (is_valid: bool, formatted_phone: str | None)
    Formatted phone will start with 62.
    """
    if not phone:
        return False, None

    cleaned = phone.replace("-", "").replace(" ", "").replace("+", "")
    pattern = r"^(62|0)[0-9]{9,12}$"
    
    if not re.match(pattern, cleaned):
        return False, None
        
    if cleaned.startswith("0"):
        formatted = "62" + cleaned[1:]
    else:
        formatted = cleaned
        
    return True, formatted


def validate_date(date_str: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate date format, ensure it's not in the future, and return formatted date.
    Returns (is_valid: bool, error_code: str | None, formatted_date: str | None)
    error_code can be 'invalid_format' or 'future_date'.
    """

    indonesian_months = {
        "januari": "January", "februari": "February", "maret": "March",
        "april": "April", "mei": "May", "juni": "June",
        "juli": "July", "agustus": "August", "september": "September",
        "oktober": "October", "november": "November", "desember": "December"
    }

    date_str_lower = date_str.lower()
    for id_month, en_month in indonesian_months.items():
        if id_month in date_str_lower:
            date_str = date_str_lower.replace(id_month, en_month)
            break 

    formats = ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d %B %Y", "%d %b %Y"]
    current_date = datetime.now()

    parsed_date = None
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str.strip(), fmt)
            break
        except ValueError:
            continue

    if parsed_date is None:
        return False, "invalid_format", None

    if not (1900 <= parsed_date.year):
        return False, "invalid_format", None

    if parsed_date > current_date:
        return False, "future_date", None

    return True, None, parsed_date.strftime("%d-%m-%Y")


def validate_location(location_name: str) -> Tuple[bool, str]:
    """
    Validate Indonesian location by checking against a static list of cities/regencies.
    Returns (is_valid: bool, clean_name: str)
    """

    ALIAS_MAP = {
        "jakarta": "Kota Jakarta Pusat",
        "jogja": "Kota Yogyakarta",
        "yogya": "Kota Yogyakarta",
        "ujung pandang": "Kota Makassar"
    }

    normalized_input = location_name.strip().lower()

    if normalized_input in ALIAS_MAP:
        return True, ALIAS_MAP[normalized_input]

    normalized_input = normalized_input.replace(".", " ")
    normalized_input = re.sub(r'\bkab\b', 'kabupaten', normalized_input)
    normalized_input = re.sub(r'\bkodya\b', 'kota', normalized_input)
    normalized_input = re.sub(r'\s+', ' ', normalized_input).strip()
    
    matched_location = None
    
    for loc in INDONESIA_CITIES_AND_REGENCIES:
        if loc.lower() == normalized_input:
            matched_location = loc
            break
    
    if not matched_location:
        matches = []
        for loc in INDONESIA_CITIES_AND_REGENCIES:
            clean_loc = loc.lower().replace("kabupaten ", "").replace("kota ", "")
            if normalized_input == clean_loc:
                matches.append(loc)

        if matches:
            kota_match = next((m for m in matches if m.startswith("Kota")), None)
            matched_location = kota_match if kota_match else matches[0]

    if matched_location:
        return True, matched_location

    return False, location_name