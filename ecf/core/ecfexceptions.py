class ECFAPIError(Exception):
    """Generic API error class."""

class ECFAPIUndefinedFunctionError(ECFAPIError):
    """Raised when attempt to call an undefined API function"""

class ECFAPIServiceNotAvailable(Exception):
    """API Service not available error class."""

class ECFINTService(Exception):
    """Generic INT Service error class."""

class ECFINTServiceNotAvailable(Exception):
    """INT Service not available error class."""

class ECFMVCService(Exception):
    """Generic MVC Service error class."""

class ECFMVCServiceNotAvailable(Exception):
    """MVC Service not available error class."""

class ECFJOBService(Exception):
    """Generic JOB Service error class."""

class ECFJOBServiceNotAvailable(Exception):
    """JOB Service not available error class."""

class ECFBOService(Exception):
    """Generic Business object service error class."""

class ECFBOServiceNotAvailable(Exception):
    """Business Object Service not available error class."""
    
class ECFImproperlyConfigured(Exception):
    "Server is somehow improperly configured"
    pass    