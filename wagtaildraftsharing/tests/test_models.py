import datetime
from textwrap import dedent
from unittest.mock import patch

import wagtail
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.timezone import is_aware
from freezegun import freeze_time
from wagtail_factories import PageFactory

import wagtaildraftsharing.models
from wagtaildraftsharing.models import WagtaildraftsharingLink

FROZEN_TIME_ISOFORMATTED = "2024-01-02 12:34:56.123456+00:00"


class TestWagtaildraftsharingLinkManager(TestCase):
    def setUp(self):
        self.test_user = User.objects.create(
            username="test", email="testuser@example.com"
        )

    def create_revision(self):
        page = PageFactory()

        # create the first revision
        page.save_revision().publish()

        old_title = page.title
        new_title = f"New {old_title}"
        page.title = new_title

        # create the second revision with a new title
        page.save_revision().publish()

        page.refresh_from_db()
        earliest_revision = page.revisions.earliest("created_at")
        return earliest_revision

    @freeze_time(FROZEN_TIME_ISOFORMATTED)
    def test_create_sharing_link_view__max_age_from_settings(self):
        frozen_time = datetime.datetime.fromisoformat(FROZEN_TIME_ISOFORMATTED)

        # Ensure we've got a level playing field: that the time is TZ-aware
        if not is_aware(frozen_time):
            self.fail("frozen_time was a naive datetime but it should not be")

        max_ages_and_expected_expiries = (
            (300, frozen_time + datetime.timedelta(seconds=300)),
            (1250000, frozen_time + datetime.timedelta(seconds=1250000)),
            (-1, None),
        )

        for max_age, expected_expiry in max_ages_and_expected_expiries:
            with self.subTest(max_age=max_age, expected_expiry=expected_expiry):
                with patch.object(
                    wagtaildraftsharing.models.draftsharing_settings, "MAX_AGE", max_age
                ):
                    revision = self.create_revision()

                    link = WagtaildraftsharingLink.objects.get_or_create_for_revision(
                        revision=revision,
                        user=self.test_user,
                    )

                    assert link.active_until == expected_expiry, (
                        link.active_until,
                        expected_expiry,
                    )

    @freeze_time(FROZEN_TIME_ISOFORMATTED)
    def test_create_sharing_link_view__max_age_from_params(self):
        frozen_time = datetime.datetime.fromisoformat(FROZEN_TIME_ISOFORMATTED)

        # Ensure we've got a level playing field: that the time is TZ-aware
        if not is_aware(frozen_time):
            self.fail("frozen_time was a naive datetime but it should not be")

        max_ages_and_expected_expiries = (
            (600, frozen_time + datetime.timedelta(seconds=600)),
            (250000, frozen_time + datetime.timedelta(seconds=250000)),
            (-1, None),
        )

        for max_age, expected_expiry in max_ages_and_expected_expiries:
            with self.subTest(max_age=max_age, expected_expiry=expected_expiry):
                revision = self.create_revision()

                link = WagtaildraftsharingLink.objects.get_or_create_for_revision(
                    revision=revision, user=self.test_user, max_age=max_age
                )

                assert link.active_until == expected_expiry, (
                    link.active_until,
                    expected_expiry,
                )


class TestWagtaildraftsharingLinkModel(TestCase):
    def create_revision(self):
        page = PageFactory()

        # create the first revision
        page.save_revision().publish()

        old_title = page.title
        new_title = f"New {old_title}"
        page.title = new_title

        # create the second revision with a new title
        page.save_revision().publish()

        page.refresh_from_db()
        earliest_revision = page.revisions.earliest("created_at")
        return earliest_revision

    def test_str_method(self):
        # Just chasing 100% coverage
        revision = self.create_revision()
        link = WagtaildraftsharingLink.objects.create(
            revision=revision,
        )
        self.assertEqual(str(link), f"Revision {revision.id} of New Test page")

    def test_url_method(self):
        link = WagtaildraftsharingLink.objects.create(
            revision=self.create_revision(),
        )
        expected_url = f"/wagtaildraftsharing/{link.key}/"
        self.assertEqual(link.url, expected_url)

    @patch.object(wagtail, "__version__", "5.0.0")  # only first digit matters
    def test_share_url_method__wagtail_5(self):
        link = WagtaildraftsharingLink.objects.create(
            revision=self.create_revision(),
        )
        expected = dedent(
            f"""<a
                class="button button-secondary button-small"
                data-wagtaildraftsharing-url
                target="_blank"
                rel="noopener noreferrer"
                href="/wagtaildraftsharing/{link.key}/">View</a>"""
        )
        self.assertEqual(dedent(link.share_url), expected)

    @patch.object(wagtail, "__version__", "6.0.0")  # only first digit matters
    def test_share_url_method__wagtail_6(self):
        link = WagtaildraftsharingLink.objects.create(
            revision=self.create_revision(),
        )
        expected = dedent(
            f"""<a
                class="button button-secondary button-small"
                data-controller="wagtaildraftsharing"
                data-wagtaildraftsharing-snippet-url
                target="_blank"
                rel="noopener noreferrer"
                href="/wagtaildraftsharing/{link.key}/">View</a>"""
        )
        self.assertEqual(dedent(link.share_url), expected)
