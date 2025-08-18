import uuid
from sqids import Sqids
from django.utils import timezone


def generate_unique_id():
    """
    Generate a unique user-friendly order id with the 
    least possible chance of collision.
    The ID will use the format `YYMMDDHHMM-<random bits>`.
    The first part (YYMMDDHHMM) which represents the year
    down to the minute will then be encoded using the squid
    library, and the final part will be cut out of a regular
    UUID4 hex string.
    This will help reduce the amount of collision per minute a day.
    """

    timestamp = timezone.now()
    year = timestamp.strftime("%y")
    month = timestamp.strftime("%m").lstrip("0") # remove leading 0 in a cross platform compactible way
    other = timestamp.strftime("%d%H%M")
    timestamp = f"{year}{month}{other}"

    uuid_suffix = uuid.uuid4().hex[:6].upper()

    sqids = Sqids(min_length=4, alphabet="ABCDEFGHIJKLMNPRSTUVWXYZ1234567890")
    half_id = sqids.encode([int(timestamp)])
    full_id = f"{half_id.upper()}-{uuid_suffix}"
    
    return full_id

