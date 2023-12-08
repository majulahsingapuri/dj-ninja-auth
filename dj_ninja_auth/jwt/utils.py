from calendar import timegm
from datetime import timezone
from functools import wraps

from django.conf import settings
from django.utils.timezone import datetime, is_naive, make_aware

from . import exceptions


def token_error(func):
    @wraps(func)
    def _wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions.TokenError as tex:
            raise exceptions.InvalidToken(str(tex)) from tex
        except Exception as ex:
            raise ex

    return _wrap


def make_utc(dt):
    if settings.USE_TZ and is_naive(dt):
        return make_aware(dt, timezone=timezone.utc)

    return dt


def datetime_to_epoch(dt):
    return timegm(dt.utctimetuple())


def datetime_from_epoch(ts):
    return make_utc(datetime.utcfromtimestamp(ts))
