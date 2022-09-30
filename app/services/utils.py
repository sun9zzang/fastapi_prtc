from datetime import datetime

from app.core import config


def convert_string_to_datetime(data_str: str) -> datetime:
    return datetime.strptime(data_str, config.DATETIME_FORMAT_STRING)


def convert_datetime_to_string(data_datetime: datetime) -> str:
    return data_datetime.strftime(config.DATETIME_FORMAT_STRING)
