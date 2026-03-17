from datetime import datetime, timedelta


REFRESH_DAYS = 7


def is_fresh(last_updated: datetime) -> bool:
    """
    Returns True if data is still within refresh window.
    """
    if last_updated is None:
        return False

    return datetime.utcnow() - last_updated < timedelta(days=REFRESH_DAYS)


def needs_refresh(last_updated: datetime) -> bool:
    """
    Opposite of is_fresh — more readable in flows.
    """
    return not is_fresh(last_updated)
