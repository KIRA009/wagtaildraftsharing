from django.conf import settings

WAGTAIL_DRAFTSHARING_ADMIN_MENU_POSITION = getattr(
    settings, "WAGTAIL_DRAFTSHARING_ADMIN_MENU_POSITION", 200
)

WAGTAIL_DRAFTSHARING_VERBOSE_NAME = getattr(
    settings, "WAGTAIL_DRAFTSHARING_VERBOSE_NAME", "Draftsharing Link"
)

WAGTAIL_DRAFTSHARING_VERBOSE_NAME_PLURAL = getattr(
    settings, "WAGTAIL_DRAFTSHARING_VERBOSE_NAME_PLURAL", "Draftsharing Links"
)

WAGTAIL_DRAFTSHARING_MENU_ITEM_LABEL = getattr(
    settings, "WAGTAIL_DRAFTSHARING_MENU_ITEM_LABEL", "Create draft sharing link"
)
