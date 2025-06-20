from django.contrib import admin
from .models import *


class CustoProducaoInline(admin.TabularInline):
    model = CustoProducao
    extra = 1 

class CustoTransporteInline(admin.TabularInline):
    model = CustoTransporte
    extra = 1

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria')
    inlines = [CustoProducaoInline, CustoTransporteInline]

admin.site.register(Partida)
admin.site.register(JogadorPartida)
admin.site.register(Rodada)
admin.site.register(Unidade)
admin.site.register(Decisao)
admin.site.register(CustoProducao)
admin.site.register(CustoTransporte)
