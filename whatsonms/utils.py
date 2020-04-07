import pytz
import math
import re
from datetime import datetime

# TIMESTAMP_FMT = "2013-04-11 18:19:07.986"
TIMESTAMP_FMT = "%Y-%m-%d %H:%M:%S.%f"

UTC_TIMEZONE = pytz.UTC
EST_TIMEZONE = pytz.timezone('America/New_York')


def sanitize_cdata(xmlstr: str) -> str:
    """
    Some xml strings come from david with double escaped cdata (see
    david_weird_cdata.xml for an example). The closing double tag has
    to be deleted in order for xmltodict to be able to parse.
    Args:
        xmlstr: An unparsed xml string from david
    Returns: xmlstr to be parsed without cdata
    """
    CDATA_REGEX = re.compile(r'<!\[CDATA\[.*\]\]>', re.MULTILINE)

    sanitized_str = CDATA_REGEX.sub(' ', xmlstr)
    return sanitized_str


def convert_time(time_str: str) -> int:
    """
    Convert (david fmt) datetime str to Epoch time.

    Args:
        time_str: Required. Of the format YYYY-MM-DD HH:MM:SS.fff
    Returns: seconds since the Epoch
    """
    track_time = datetime.strptime(time_str, TIMESTAMP_FMT)

    track_time = EST_TIMEZONE.localize(track_time)
    track_time = track_time.astimezone(UTC_TIMEZONE)

    epoch = datetime(1970, 1, 1)
    epoch = UTC_TIMEZONE.localize(epoch)

    epoch_time = math.floor((track_time - epoch).total_seconds())

    return epoch_time


def convert_time_to_iso(epoch_timestamp: int) -> str:
    """
    Args: epoch: Required.
    Returns: ISO 8601 date and time.
    """
    utc_time = datetime.utcfromtimestamp(epoch_timestamp)
    localized_utc_time = UTC_TIMEZONE.localize(utc_time)
    iso_utc_time = localized_utc_time.isoformat()

    return iso_utc_time


def convert_date_time(date_: str, time_: str) -> int:
    """
    Convert (nexgen fmt) date str and time str to Epoch time.

    Args:
        date_: Required. Of the format MM/DD/YYYY
        time_: Required. Of the format HH:MM:SS
    Returns: seconds since the Epoch
    """
    month, day, year = date_.split('/')
    date_time = f'{year}-{month}-{day} {time_}.00'
    return convert_time(date_time)


def convert_encoding(win1252str: str) -> str:
    """
    Convert a string encoded with windows-1252 to utf8.

    Args:
        win1252str: Required. A str formatted in windows-1252
    Returns: utf8 string
    """
    encoded_str = win1252str.encode('windows-1252')
    utf_str = encoded_str.decode('utf8')
    return utf_str
