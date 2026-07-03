from .exceptions import LicenseError

HARDCODED_LICENSE_KEY = "ank@8250255103#sark_$"

def validate_license(api_key: str | None) -> bool:
    """
    Mock license validation system for v1.0.
    Expects a hardcoded key.
    """
    if not api_key:
        raise LicenseError("API key is required.")
    
    if api_key != HARDCODED_LICENSE_KEY:
        raise LicenseError("Invalid API key.")
        
    return True
