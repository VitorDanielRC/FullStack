from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import Perfil


def perfil_ativo(usuario):
    if not usuario.is_authenticated or not usuario.is_active:
        return None
    perfil = getattr(usuario, "perfil", None)
    if perfil and perfil.vendedor.ativo and perfil.papel in Perfil.Papel.values:
        return perfil
    return None


def painel_requerido(view=None, *, admin=False):
    def decorar(funcao):
        @login_required(login_url="painel:login")
        @wraps(funcao)
        def protegida(request, *args, **kwargs):
            perfil = perfil_ativo(request.user)
            if not perfil or (admin and not perfil.eh_admin):
                raise PermissionDenied("Sua conta não tem acesso a esta área do vendedor.")
            return funcao(request, perfil, *args, **kwargs)

        return protegida

    return decorar(view) if view else decorar
