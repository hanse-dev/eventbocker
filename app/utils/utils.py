from datetime import datetime
import pytz

def get_utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(pytz.UTC)
