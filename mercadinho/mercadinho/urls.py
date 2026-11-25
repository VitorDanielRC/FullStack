from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("painel/", include("loja.painel_urls")),
    path("api/", include("loja.api_urls")),
    path("api/auth/", include("rest_framework.urls")),
    path("", include("loja.urls")),
]