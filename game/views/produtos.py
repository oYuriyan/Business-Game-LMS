from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from game.models.produtos import Produto

@staff_member_required
def listar_produtos(request):
    
        produtos = Produto.objects.all()
        return render(request, 'produtos.html', {'produtos': produtos})

def criar_produto(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        preco = request.POST.get('preco')
        quantidade = request.POST.get('quantidade')

        Produto.objects.create(nome=nome, quantidade=quantidade, preco=preco)
        messages.success(request, 'Produto criado com sucesso!')

        return redirect('listar_produtos')
    return render(request, 'criar_produto.html')

def editar_produto(request, produto_id): 
    produto = get_object_or_404(Produto, id=produto_id)
    if request.method == 'POST':
        produto.nome = request.POST.get('nome')
        produto.quantidade = request.POST.get('quantidade')
        produto.preco = request.POST.get('preco')
        produto.save()

        messages.success(request, 'Produto atualizado com sucesso!')
        return redirect('listar_produtos')
    return render(request, 'editar_produto.html', {'produto' : produto})

def excluir_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    produto.delete()
    messages.success(request, 'Produto excluído com sucesso!')
    return redirect('listar_produtos')
    
