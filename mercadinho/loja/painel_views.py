import csv

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST

from .acesso import painel_requerido
from .catalogo import filtrar_produtos
from .dashboard import metricas, pedidos_do_vendedor
from .forms import CupomForm, PeriodoForm, ProdutoForm, StatusEntregaForm
from .models import PedidoVendedor, Produto
from .services import atualizar_status_entrega


CATALOGO = {
    "produtos": (ProdutoForm, "Produtos", "produto"),
    "cupons": (CupomForm, "Cupons", "cupom"),
}


def _pagina(request, objetos):
    return Paginator(objetos, 25).get_page(request.GET.get("pagina"))


def _recurso_catalogo(recurso, perfil):
    if recurso not in CATALOGO:
        raise Http404
    if recurso == "cupons" and not perfil.eh_admin:
        raise PermissionDenied
    form_class, titulo, singular = CATALOGO[recurso]
    objetos = form_class._meta.model.objects.filter(vendedor_id=perfil.vendedor_id).order_by("pk")
    return form_class, titulo, singular, objetos


@never_cache
@painel_requerido
def dashboard(request, perfil):
    form = PeriodoForm(request.GET)
    dados = None
    if form.is_valid():
        dados = metricas(pedidos_do_vendedor(perfil.vendedor_id, form.cleaned_data), perfil.eh_admin)
    return render(request, "loja/painel/dashboard.html", {"perfil": perfil, "form": form, "dados": dados})


@never_cache
@painel_requerido(admin=True)
def exportar(request, perfil):
    form = PeriodoForm(request.GET)
    if not form.is_valid():
        return HttpResponse("Período inválido.", status=400, content_type="text/plain; charset=utf-8")
    pedidos = pedidos_do_vendedor(perfil.vendedor_id, form.cleaned_data).select_related("pedido")
    resposta = HttpResponse("\ufeff", content_type="text/csv; charset=utf-8")
    resposta["Content-Disposition"] = 'attachment; filename="pedidos.csv"'
    escritor = csv.writer(resposta, delimiter=";")
    escritor.writerow(["Pedido", "Data", "Status", "Subtotal (R$)", "Desconto (R$)", "Total (R$)"])
    for entrega in pedidos.order_by("-pedido__criado_em", "pk").iterator():
        escritor.writerow([
            entrega.pedido.numero,
            timezone.localtime(entrega.pedido.criado_em).strftime("%d/%m/%Y %H:%M"),
            entrega.get_status_display(),
            *[format(valor, ".2f").replace(".", ",") for valor in (entrega.subtotal, entrega.desconto, entrega.total)],
        ])
    return resposta


@never_cache
@painel_requerido
def pedidos(request, perfil):
    entregas = PedidoVendedor.objects.filter(vendedor_id=perfil.vendedor_id)
    entregas = entregas.select_related("pedido").order_by("-pedido__criado_em", "pk")
    return render(request, "loja/painel/pedidos.html", {"perfil": perfil, "pagina": _pagina(request, entregas)})


@never_cache
@painel_requerido
@require_http_methods(["GET", "POST"])
def pedido(request, perfil, pk):
    entregas = PedidoVendedor.objects.select_related("pedido").prefetch_related("itens")
    entrega = get_object_or_404(entregas, pk=pk, vendedor_id=perfil.vendedor_id)
    form = StatusEntregaForm(request.POST if request.method == "POST" else None, initial={"status": entrega.status})
    if request.method == "POST" and form.is_valid():
        atualizar_status_entrega(entrega, form.cleaned_data["status"])
        messages.success(request, "Status da entrega atualizado.")
        return redirect("painel:pedido", pk=pk)
    return render(request, "loja/painel/pedido.html", {"perfil": perfil, "entrega": entrega, "form": form})


@never_cache
@painel_requerido
def catalogo(request, perfil, recurso):
    _, titulo, singular, objetos = _recurso_catalogo(recurso, perfil)
    filtros = {}
    if recurso == "produtos":
        objetos, busca, categoria = filtrar_produtos(objetos, request.GET)
        filtros = {"busca": busca, "categoria_ativa": categoria, "categorias": Produto.Categoria.choices}
    return render(request, "loja/painel/catalogo.html", {
        "perfil": perfil, "titulo": titulo, "singular": singular, "recurso": recurso,
        "pagina": _pagina(request, objetos), **filtros,
    })


@never_cache
@painel_requerido(admin=True)
@require_http_methods(["GET", "POST"])
def editar(request, perfil, recurso, pk=None):
    form_class, _, singular, objetos = _recurso_catalogo(recurso, perfil)
    if request.method == "POST":
        with transaction.atomic():
            instancia = (
                get_object_or_404(objetos.select_for_update(), pk=pk) if pk is not None
                else objetos.model(vendedor_id=perfil.vendedor_id)
            )
            form = form_class(request.POST, instance=instancia)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        form.save()
                except IntegrityError:
                    form.add_error(None, "O identificador já está em uso. Escolha outro e tente novamente.")
                else:
                    messages.success(request, "Alterações salvas.")
                    return redirect("painel:catalogo", recurso=recurso)
    else:
        instancia = get_object_or_404(objetos, pk=pk) if pk is not None else None
        form = form_class(instance=instancia)
    return render(request, "loja/painel/editar.html", {
        "perfil": perfil, "form": form, "singular": singular, "recurso": recurso, "pk": pk,
    })


@painel_requerido(admin=True)
@require_POST
def excluir(request, perfil, recurso, pk):
    _, _, _, objetos = _recurso_catalogo(recurso, perfil)
    objeto = get_object_or_404(objetos, pk=pk)
    try:
        objeto.delete()
    except IntegrityError:
        messages.error(request, "Este registro está ligado a pedidos e pode apenas ser desativado.")
    else:
        messages.success(request, "Registro excluído.")
    return redirect("painel:catalogo", recurso=recurso)
