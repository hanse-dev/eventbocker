from datetime import datetime
import pytz
import traceback
from flask import current_app
from sqlalchemy.exc import OperationalError

def get_utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(pytz.UTC)

def log_db_error(context: str, error: Exception) -> None:
    """Log a database error, flagging SQLite lock contention distinctly.

    SQLite 'database is locked' errors get a fixed SQLITE_LOCK_ERROR prefix
    so they can be grepped/counted/alerted on separately from other DB
    failures (e.g. to check whether the nightly restart is still needed).
    """
    if isinstance(error, OperationalError) and 'database is locked' in str(error).lower():
        current_app.logger.error(
            f"SQLITE_LOCK_ERROR bei {context}: {error}\n{traceback.format_exc()}"
        )
    else:
        current_app.logger.error(f"{context}: {error}\n{traceback.format_exc()}")
