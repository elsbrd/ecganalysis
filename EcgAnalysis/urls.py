from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/",
        include(
            [
                path("modelling/", include("modelling.urls")),
                path("analysis/", include("analysis.urls")),
            ]
        ),
    ),
]

urlpatterns += [path("", TemplateView.as_view(template_name="index.html"))]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
