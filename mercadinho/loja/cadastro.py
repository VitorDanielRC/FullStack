from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProdutoCadastroForm
from .models import Produto


def catalogo(request):
    produtos = Produto.objects.filter(
        ativo=True,
        vendedor__ativo=True,
    ).select_related("vendedor")

    return render(
        request,
        "loja/catalogo.html",
        {"produtos": produtos},
    )


def cadastrar_produto(request):
    form = ProdutoCadastroForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Produto cadastrado com sucesso.")
        return redirect("loja:catalogo")

    return render(
        request,
        "loja/cadastrar_produto.html",
        {
            "form": form,
            "titulo": "Cadastrar produto",
            "texto_botao": "Cadastrar produto",
        },
    )


def editar_produto(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    form = ProdutoCadastroForm(request.POST or None, produto=produto)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Produto alterado com sucesso.")
        return redirect("loja:catalogo")

    return render(
        request,
        "loja/cadastrar_produto.html",
        {
            "form": form,
            "titulo": "Editar produto",
            "texto_botao": "Salvar alterações",
        },
    )