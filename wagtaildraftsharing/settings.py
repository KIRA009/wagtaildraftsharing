import dataclasses
from typing import cast

from django.conf import settings as django_settings
from django.utils.functional import SimpleLazyObject

_DEFAULT_MAX_TTL = 28 * 24 * 60 * 60  # 28 days


@dataclasses.dataclass
class WagtaildraftsharingSettings:
    ADMIN_MENU_POSITION: int = 200
    VERBOSE_NAME: str = "Draftsharing Link"
    VERBOSE_NAME_PLURAL: str = "Draftsharing Links"
    MENU_ITEM_LABEL: str = "Create draft sharing link"
    MAX_TTL: int = _DEFAULT_MAX_TTL


def _init_settings():
    """
    Get and validate Wagtaildraftsharing settings from the Django settings.
    """

    setting_name = "WAGTAILDRAFTSHARING"
    django_settings_dict = getattr(django_settings, setting_name, {})

    overriden_defaults = {}

    for optional_setting_name in [
        "ADMIN_MENU_POSITION",
        "VERBOSE_NAME",
        "VERBOSE_NAME_PLURAL",
        "MENU_ITEM_LABEL",
        "MAX_TTL",
    ]:
        if optional_setting_name in django_settings_dict:
            overriden_defaults[optional_setting_name] = django_settings_dict[
                optional_setting_name
            ]

    return WagtaildraftsharingSettings(**overriden_defaults)


settings = cast(WagtaildraftsharingSettings, SimpleLazyObject(_init_settings))
