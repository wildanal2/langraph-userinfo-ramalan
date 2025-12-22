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
    Strict location validation: Must be in Indonesia & Must be Administrative Region.
    Returns: (is_valid: bool, formatted_name: str)
    """
    geolocator = Nominatim(user_agent="ekraf_bot_validator_v2")
    
    try:
        location = geolocator.geocode(location_name, language='id', addressdetails=True)
        
        if not location:
            return False, location_name
            
        raw_data = location.raw
        address = raw_data.get('address', {})
        
        if address.get('country_code') != 'id':
            # Opsional: Bisa return False atau biarkan kalau mau support global
            return False, location_name 
            
        invalid_classes = ['amenity', 'shop', 'tourism', 'highway', 'man_made', 'leisure', 'office']
        if raw_data.get('class') in invalid_classes:
            return False, location_name

        valid_keys = ['city', 'town', 'village', 'county', 'state', 'municipality', 'suburb', 'neighbourhood', 'district']
        
        found_key = next((k for k in valid_keys if k in address), None)
        
        if found_key:
            clean_name = address[found_key]
            
            if found_key in ['suburb', 'neighbourhood', 'village']:
                parent = address.get('city') or address.get('county') or address.get('state')
                if parent:
                    clean_name = f"{clean_name}, {parent}"
            
            return True, clean_name
            
        return False, location_name

    except (GeocoderTimedOut, GeocoderServiceError):
        return True, location_name 
    except Exception as e:
        return True, location_name