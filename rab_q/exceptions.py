class RabQError(Exception):
    """Base exception for all rab_q errors."""
    pass

class ConfigurationError(RabQError):
    """Raised when there is a configuration error."""
    pass

class LicenseError(RabQError):
    """Raised when license validation fails."""
    pass

class ConnectionError(RabQError):
    """Raised when unable to connect to the message broker."""
    pass
