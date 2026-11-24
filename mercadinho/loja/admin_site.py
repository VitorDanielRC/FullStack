from django.contrib.admin import AdminSite
from django.contrib.admin.apps import AdminConfig


class PlataformaAdminSite(AdminSite):
    site_header = "Administração do Mercado da Vila"

    def has_permission(self, request):
        return super().has_permission(request) and request.user.is_superuser


class PlataformaAdminConfig(AdminConfig):
    default_site = "loja.admin_site.PlataformaAdminSite"
