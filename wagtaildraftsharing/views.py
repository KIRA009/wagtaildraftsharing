from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from wagtail.admin.auth import user_has_any_page_permission, user_passes_test
from wagtail.admin.views.generic.preview import PreviewRevision
from wagtail.models import Page, Revision

from wagtaildraftsharing.forms import CreateWagtaildraftsharingLinkForm
from wagtaildraftsharing.models import WagtaildraftsharingLink
from wagtaildraftsharing.utils import tz_aware_utc_now


class SharingLinkView(PreviewRevision):
    def setup(self, request, *args, **kwargs):
        key = kwargs.pop("key")
        now = tz_aware_utc_now()

        sharing_link = get_object_or_404(
            WagtaildraftsharingLink,
            key=key,
            is_active=True,
        )
        if sharing_link.active_until and sharing_link.active_until < now:
            sharing_link.is_active = False
            sharing_link.save(update_fields=["is_active"])
            raise Http404

        revision_id = sharing_link.revision_id
        page_id = get_object_or_404(Revision, id=revision_id).object_id
        return super().setup(request, *args, page_id, revision_id, **kwargs)

    def get_object(self):
        return get_object_or_404(Page, id=self.pk).specific


@method_decorator(user_passes_test(user_has_any_page_permission), name="dispatch")
class CreateSharingLinkView(CreateView):
    model = WagtaildraftsharingLink
    form_class = CreateWagtaildraftsharingLinkForm

    def form_valid(self, form):
        sharing_link = WagtaildraftsharingLink.objects.get_or_create_for_revision(
            revision=form.cleaned_data["revision"],
            user=self.request.user,
        )
        return JsonResponse({"url": sharing_link.url})

    def form_invalid(self, form):
        return JsonResponse({"errors": form.errors}, status=400)
