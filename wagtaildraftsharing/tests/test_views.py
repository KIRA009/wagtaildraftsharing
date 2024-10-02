import datetime
import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import Http404
from django.test import RequestFactory, TestCase, override_settings
from django.utils.timezone import now as datetime_now
from freezegun import freeze_time
from wagtail_factories import PageFactory

import wagtaildraftsharing.views
from wagtaildraftsharing.models import WagtaildraftsharingLink
from wagtaildraftsharing.views import CreateSharingLinkView, SharingLinkView

User = get_user_model()

FROZEN_TIME_ISOFORMATTED = "2024-01-02 12:34:56.123456+00:00"


class TestViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.superuser = User.objects.create_superuser(username="test", password="test")
        cls.factory = RequestFactory()

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

    def test_create_sharing_link_view(self):
        revision = self.create_revision()
        request = self.factory.post(
            "/create/",
            {
                "revision": revision.id,
            },
        )
        request.user = self.superuser

        response = CreateSharingLinkView.as_view()(request)
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(
            response_data["url"], WagtaildraftsharingLink.objects.get().url
        )

    @freeze_time(FROZEN_TIME_ISOFORMATTED)
    def test_create_sharing_link_view__max_age_from_settings(self):
        frozen_time = datetime.datetime.fromisoformat(FROZEN_TIME_ISOFORMATTED)

        max_ages_and_expected_expiries = (
            (300, frozen_time + datetime.timedelta(seconds=300)),
            (1250000, frozen_time + datetime.timedelta(seconds=1250000)),
            (-1, None),
        )

        for max_age, expected_expiry in max_ages_and_expected_expiries:
            with self.subTest(max_age=max_age, expected_expiry=expected_expiry):
                with patch.object(wagtaildraftsharing.views, "max_age", max_age):
                    revision = self.create_revision()
                    request = self.factory.post("/create/", {"revision": revision.id})
                    request.user = self.superuser

                    response = CreateSharingLinkView.as_view()(request)
                    self.assertEqual(response.status_code, 200)

                    link = WagtaildraftsharingLink.objects.last()
                    assert link.active_until == expected_expiry, (
                        link.active_until,
                        expected_expiry,
                    )

    def test_sharing_link_view__valid_link(self):
        revision = self.create_revision()
        sharing_link = WagtaildraftsharingLink.objects.create(
            revision=revision, created_by=self.superuser
        )

        request = self.factory.get(f"/{sharing_link.key}/")
        response = SharingLinkView.as_view()(request, key=sharing_link.key)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"<title>{revision.as_object().title}</title>")

    def test_sharing_link_view__invalid_link_404s(self):
        revision = self.create_revision()
        sharing_link = WagtaildraftsharingLink.objects.create(
            revision=revision, created_by=self.superuser
        )

        dummy_key = "336611cb-c2aa-4e2b-9b52-1d183939cbf8"
        assert sharing_link.key != dummy_key  # Extremely unlikely to clash!

        request = self.factory.get(f"/{dummy_key}/")
        with self.assertRaises(Http404):
            SharingLinkView.as_view()(request, key=dummy_key)

    def test_sharing_link_view__expired_link_404s_and_sets_is_active_to_False(self):
        revision = self.create_revision()
        sharing_link = WagtaildraftsharingLink.objects.create(
            revision=revision, created_by=self.superuser
        )
        request = self.factory.get(f"/{sharing_link.key}/")
        assert sharing_link.is_active is True

        response = SharingLinkView.as_view()(request, key=sharing_link.key)
        self.assertEqual(response.status_code, 200)

        sharing_link.active_until = datetime_now() - datetime.timedelta(seconds=1)
        sharing_link.save()
        sharing_link.refresh_from_db()

        assert sharing_link.is_active is True  # still true until it's called

        with self.assertRaises(Http404):
            SharingLinkView.as_view()(request, key=sharing_link.key)

        sharing_link.refresh_from_db()
        assert sharing_link.is_active is False  # calling it after expiry deactivates it

    def test_sharing_link_view__inactive_link_404s(self):
        revision = self.create_revision()
        sharing_link = WagtaildraftsharingLink.objects.create(
            revision=revision, created_by=self.superuser, is_active=False
        )
        request = self.factory.get(f"/{sharing_link.key}/")
        with self.assertRaises(Http404):
            SharingLinkView.as_view()(request, key=sharing_link.key)
