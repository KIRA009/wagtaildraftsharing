import json
from unittest.mock import Mock, patch

import wagtail
from django.test import RequestFactory, TestCase
from django.urls import reverse

from wagtaildraftsharing import wagtail_hooks


class WagtailHooksTests(TestCase):
    def test_editor_js(self):
        self.maxDiff = None
        for wagtail_version, expected in (
            (
                "5.0.0",  # only major version matters
                # Whitespace here is horrible. TODO: improve
                f"""<script src="/static/wagtaildraftsharing/js/wagtaildraftsharing.js"></script>
        <script id="wagtaildraftsharing-config" type="application/json">
            {json.dumps({
                'urls': {
                    'create': reverse('wagtaildraftsharing:create'),
                },
            })}
        </script>""",  # NOQA: E501
            ),
            (
                "6.0.0",  # only major version matters
                # Whitespace here is horrible. TODO: improve
                f"""<script type="module" src="/static/wagtaildraftsharing/js/wagtaildraftsharing_controller.js"></script>
        <script id="wagtaildraftsharing-config" type="application/json">
            {json.dumps({
                'urls': {
                    'create': reverse('wagtaildraftsharing:create'),
                },
            })}
        </script>""",  # NOQA: E501
            ),
        ):
            with self.subTest(wagtail_version=wagtail_version, expected=expected):
                with patch.object(wagtail, "__version__", wagtail_version):
                    js_tags = wagtail_hooks.editor_js()
                    self.assertEqual(js_tags, expected)

    def test_action_menu_hook__get_context_data(self):
        req = RequestFactory().get("/path/is/not/relevant/")

        mock_revision = Mock(name="mock_revision")

        mock_page = Mock(name="mock_page")
        mock_page.latest_revision = mock_revision
        menu_item = wagtail_hooks.DraftsharingPageActionMenuItem()

        self.assertEqual(
            menu_item.get_context_data(
                parent_context={"request": req, "page": mock_page}
            ),
            {
                "classname": "",
                "icon_name": "view",
                "label": "Create draft sharing link",
                "name": "action-draftsharing",
                "page": mock_page,
                "request": req,
                "revision": mock_revision,
                "url": None,
            },
        )

    def test_action_menu_hook__is_shown(self):
        mock_page = Mock(name="mock_page")
        menu_item = wagtail_hooks.DraftsharingPageActionMenuItem()

        mock_page.has_unpublished_changes = False
        self.assertFalse(menu_item.is_shown({"page": mock_page}))

        mock_page.has_unpublished_changes = True
        self.assertTrue(menu_item.is_shown({"page": mock_page}))

    def test_action_menu_hook__is_shown__no_page_in_context(self):
        menu_item = wagtail_hooks.DraftsharingPageActionMenuItem()
        self.assertFalse(menu_item.is_shown({}))
        self.assertFalse(menu_item.is_shown({"something_that_is_not_a_page": "here"}))
