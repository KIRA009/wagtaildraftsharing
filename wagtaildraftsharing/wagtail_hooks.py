import json

import wagtail
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from wagtail import hooks
from wagtail.admin.action_menu import ActionMenuItem
from wagtail.snippets.models import register_snippet

from wagtaildraftsharing.actions import (
    register_wagtaildraftsharing_log_actions,
)
from wagtaildraftsharing.snippets import WagtaildraftsharingLinkSnippetViewSet

from .settings import settings as draftsharing_settings

register_snippet(WagtaildraftsharingLinkSnippetViewSet)

hooks.register("register_log_actions")(register_wagtaildraftsharing_log_actions)


@hooks.register("insert_global_admin_js")
def editor_js():
    # We need different approaches to the JS depending on whether it's
    # Wagtail 5 (vanilla JS) or Wagtail 6 (Stimulus)
    if int(wagtail.__version__[0]) < 6:
        SHARING_JS_TEMPLATE = """<script src="{}"></script>"""
        SHARING_JS_PATH = "wagtaildraftsharing/js/wagtaildraftsharing.js"
    else:
        SHARING_JS_TEMPLATE = """<script type="module" src="{}"></script>"""
        SHARING_JS_PATH = "wagtaildraftsharing/js/wagtaildraftsharing_controller.js"

    return format_html(
        SHARING_JS_TEMPLATE,
        static(SHARING_JS_PATH),
    ) + mark_safe(
        f"""
        <script id="wagtaildraftsharing-config" type="application/json">
            {json.dumps({
                'urls': {
                    'create': reverse('wagtaildraftsharing:create'),
                },
            })}
        </script>"""
    )


class DraftsharingPageActionMenuItem(ActionMenuItem):
    # Adds a button for sharing a draft to the bottom-of-page action menu
    # when a page is being edited, but only if there is a saved draft to share
    order = 1600
    name = "action-draftsharing"
    icon_name = "view"
    label = draftsharing_settings.MENU_ITEM_LABEL

    template_name = "wagtaildraftsharing/action_menu_item.html"

    def get_context_data(self, parent_context):
        context_data = super().get_context_data(parent_context)

        context_data["revision"] = context_data["page"].latest_revision
        return context_data

    def is_shown(self, context):
        return "page" in context and context["page"].has_unpublished_changes


@hooks.register("register_page_action_menu_item")
def register_draftsharing_page_action_menu_item():
    return DraftsharingPageActionMenuItem()
