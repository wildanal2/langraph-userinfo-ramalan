import asyncio
import re
from datetime import datetime
from typing import Tuple, Optional
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
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate Indonesian phone number"""
    cleaned = phone.replace("-", "").replace(" ", "").replace("+", "")
    pattern = r"^(62|0)[0-9]{9,12}$"
    return bool(re.match(pattern, cleaned))


def validate_date(date_str: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate date format, ensure it's not in the future, and return formatted date.
    Returns (is_valid: bool, error_code: str | None, formatted_date: str | None)
    error_code can be 'invalid_format' or 'future_date'.
    """
    
    # Mapping for Indonesian months to English for parsing
    indonesian_months = {
        "januari": "January", "februari": "February", "maret": "March",
        "april": "April", "mei": "May", "juni": "June",
        "juli": "July", "agustus": "August", "september": "September",
        "oktober": "October", "november": "November", "desember": "December"
    }

    # Normalize input: lowercase and replace Indonesian months
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


async def validate_location(location_name: str) -> Tuple[bool, str]:
    """
    Validate Indonesian location using geopy and Nominatim.
    Returns (is_valid: bool, clean_name: str)
    """
    geolocator = Nominatim(user_agent="ekraf_bot")

    def geocode_sync():
        try:
            return geolocator.geocode(location_name, language="id", addressdetails=True)
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"[WARNING] Geocoding service failed for '{location_name}': {e}")
            return None # Return None on geocoding service errors

    try:
        location = await asyncio.to_thread(geocode_sync)

        if not location:
            # Be lenient on geocoding failure, accept user input
            return True, location_name

        raw_data = location.raw
        address = raw_data.get("address", {})

        if address.get("country_code") != "id":
            return False, location_name

        detected_type = raw_data.get("addresstype") or raw_data.get("type")

        valid_types = ["city", "county"]

        if detected_type not in valid_types:
            return False, location_name

        clean_name = (
            address.get("city") or address.get("county")
        )

        if not clean_name:
            clean_name = location.address.split(",")[0]

        return True, clean_name

    except Exception as e:
        print(f"[ERROR] Location Validation Fail: {e}")
        return True, location_name