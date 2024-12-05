from django.conf import settings
from django.urls import include, path

from wagtail.admin import urls as wagtailadmin_urls

import wagtaildraftsharing.urls as wagtaildraftsharing_urls


urlpatterns = [
    path("admin/", include(wagtailadmin_urls)),
    path("wagtaildraftsharing/", include(wagtaildraftsharing_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
