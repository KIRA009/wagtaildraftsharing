from datetime import timezone

from django.utils.timezone import is_aware, make_aware
from django.utils.timezone import now as timezone_now


def tz_aware_utc_now():
    now = timezone_now()
    # Depending on your version of Django and/or setting.TZ_NOW, timezone_now()
    # may not actually be TZ aware, but we always want it to be for these links
    if not is_aware(now):
        now = make_aware(now, timezone.utc)
    return now
