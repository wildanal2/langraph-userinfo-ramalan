import re
from datetime import datetime
from typing import Tuple 
from geopy.geocoders import Nominatim 
from geopy.exc import GeocoderTimedOut, GeocoderServiceError 

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

def validate_location(location_name: str) -> Tuple[bool, str]:
    """
    Validate Indonesian location using geopy and Nominatim.
    Returns (is_valid: bool, clean_name: str)
    """
    geolocator = Nominatim(user_agent="ekraf_bot")
    
    try:
        location = geolocator.geocode(location_name, language='id', addressdetails=True)
        
        if not location:
            return False, location_name
            
        raw_data = location.raw
        address = raw_data.get('address', {})

        if address.get('country_code') != 'id':
            return False, location_name

        detected_type = raw_data.get('addresstype') or raw_data.get('type')
        
        valid_types = ['city', 'county', 'municipality']
        
        if detected_type not in valid_types:
            return False, location_name

        clean_name = address.get('city') or address.get('county') or address.get('municipality')
        
        if not clean_name:
            clean_name = location.address.split(',')[0]
            
        return True, clean_name

    except Exception as e:
        print(f"[ERROR] Location Validation Fail: {e}")
        return True, location_name
