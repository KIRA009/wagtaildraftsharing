from django.utils.translation import gettext_lazy as _
from wagtail.log_actions import LogFormatter

WAGTAILDRAFTSHARING_CREATE_SHARING_LINK = "wagtaildraftsharing.create_sharing_link"
WAGTAILDRAFTSHARING_REUSE_SHARING_LINK = "wagtaildraftsharing.reuse_sharing_link"


def register_wagtaildraftsharing_log_actions(actions):
    @actions.register_action(WAGTAILDRAFTSHARING_CREATE_SHARING_LINK)
    class CreateSharingLink(LogFormatter):
        label = _("Create sharing link")

        def format_message(self, log_entry):
            return _(
                "{username} created sharing link for revision {revision_id}"
            ).format(
                revision_id=log_entry.data["revision"],
                username=log_entry.user,
            )

    @actions.register_action(WAGTAILDRAFTSHARING_REUSE_SHARING_LINK)
    class ReuseSharingLink(LogFormatter):
        label = _("Reuse sharing link")

        def format_message(self, log_entry):
            return _(
                "{username} reused sharing link for revision {revision_id}"
            ).format(
                revision_id=log_entry.data["revision"],
                username=log_entry.user,
            )
