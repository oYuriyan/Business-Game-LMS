from decimal import Decimal

CUSTOS_PRODUCAO_PADRAO = {
    'Empresa A': {'Cafeteira': Decimal('30.00'), 'Torradeira': Decimal('40.00')},
    'Empresa B': {'Cafeteira': Decimal('29.00'), 'Torradeira': Decimal('41.00')},
    'Empresa C': {'Cafeteira': Decimal('31.00'), 'Torradeira': Decimal('40.00')},
    'Empresa D': {'Cafeteira': Decimal('30.00'), 'Torradeira': Decimal('39.00')},
}

ESTOQUES_INICIAIS_PADRAO = {
    'Empresa A': {
        'Cafeteira': {'Unidade 1': 100, 'Unidade 2': 80, 'Unidade 3': 50},
        'Torradeira': {'Unidade 1': 80, 'Unidade 2': 50, 'Unidade 3': 40},
    },
    'Empresa B': {
        'Cafeteira': {'Unidade 1': 100, 'Unidade 2': 80, 'Unidade 3': 50},
        'Torradeira': {'Unidade 1': 80, 'Unidade 2': 50, 'Unidade 3': 40},
    },
    'Empresa C': {
        'Cafeteira': {'Unidade 1': 100, 'Unidade 2': 80, 'Unidade 3': 50},
        'Torradeira': {'Unidade 1': 80, 'Unidade 2': 50, 'Unidade 3': 40},
    },
    'Empresa D': {
        'Cafeteira': {'Unidade 1': 100, 'Unidade 2': 80, 'Unidade 3': 50},
        'Torradeira': {'Unidade 1': 80, 'Unidade 2': 50, 'Unidade 3': 40},
    }
}

CUSTOS_TRANSPORTE_PADRAO = [
    # EMPRESA A
    # Cafeteira
    {'empresa': 'Empresa A', 'produto': 'Cafeteira', 'origem': 'Unidade 1', 'destino': 'São Paulo', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa A', 'produto': 'Cafeteira', 'origem': 'Unidade 1', 'destino': 'Osasco', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa A', 'produto': 'Cafeteira', 'origem': 'Unidade 1', 'destino': 'Taboão', 'custo': Decimal('3.00')},
    {'empresa': 'Empresa A', 'produto': 'Cafeteira', 'origem': 'Unidade 2', 'destino': 'São Paulo', 'custo': Decimal('3.00')},
    {'empresa': 'Empresa A', 'produto': 'Cafeteira', 'origem': 'Unidade 2', 'destino': 'Osasco', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa A', 'produto': 'Cafeteira', 'origem': 'Unidade 2', 'destino': 'Taboão', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa A', 'produto': 'Cafeteira', 'origem': 'Unidade 3', 'destino': 'São Paulo', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa A', 'produto': 'Cafeteira', 'origem': 'Unidade 3', 'destino': 'Osasco', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa A', 'produto': 'Cafeteira', 'origem': 'Unidade 3', 'destino': 'Taboão', 'custo': Decimal('1.00')},
    # Torradeira
    {'empresa': 'Empresa A', 'produto': 'Torradeira', 'origem': 'Unidade 1', 'destino': 'São Paulo', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa A', 'produto': 'Torradeira', 'origem': 'Unidade 1', 'destino': 'Osasco', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa A', 'produto': 'Torradeira', 'origem': 'Unidade 1', 'destino': 'Taboão', 'custo': Decimal('3.00')},
    {'empresa': 'Empresa A', 'produto': 'Torradeira', 'origem': 'Unidade 2', 'destino': 'São Paulo', 'custo': Decimal('3.00')},
    {'empresa': 'Empresa A', 'produto': 'Torradeira', 'origem': 'Unidade 2', 'destino': 'Osasco', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa A', 'produto': 'Torradeira', 'origem': 'Unidade 2', 'destino': 'Taboão', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa A', 'produto': 'Torradeira', 'origem': 'Unidade 3', 'destino': 'São Paulo', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa A', 'produto': 'Torradeira', 'origem': 'Unidade 3', 'destino': 'Osasco', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa A', 'produto': 'Torradeira', 'origem': 'Unidade 3', 'destino': 'Taboão', 'custo': Decimal('1.00')},
    
    # EMPRESA B
    # Cafeteira
    {'empresa': 'Empresa B', 'produto': 'Cafeteira', 'origem': 'Unidade 1', 'destino': 'São Paulo', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa B', 'produto': 'Cafeteira', 'origem': 'Unidade 1', 'destino': 'Osasco', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa B', 'produto': 'Cafeteira', 'origem': 'Unidade 1', 'destino': 'Taboão', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa B', 'produto': 'Cafeteira', 'origem': 'Unidade 2', 'destino': 'São Paulo', 'custo': Decimal('3.00')},
    {'empresa': 'Empresa B', 'produto': 'Cafeteira', 'origem': 'Unidade 2', 'destino': 'Osasco', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa B', 'produto': 'Cafeteira', 'origem': 'Unidade 2', 'destino': 'Taboão', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa B', 'produto': 'Cafeteira', 'origem': 'Unidade 3', 'destino': 'São Paulo', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa B', 'produto': 'Cafeteira', 'origem': 'Unidade 3', 'destino': 'Osasco', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa B', 'produto': 'Cafeteira', 'origem': 'Unidade 3', 'destino': 'Taboão', 'custo': Decimal('1.00')},
    # Torradeira
    {'empresa': 'Empresa B', 'produto': 'Torradeira', 'origem': 'Unidade 1', 'destino': 'São Paulo', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa B', 'produto': 'Torradeira', 'origem': 'Unidade 1', 'destino': 'Osasco', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa B', 'produto': 'Torradeira', 'origem': 'Unidade 1', 'destino': 'Taboão', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa B', 'produto': 'Torradeira', 'origem': 'Unidade 2', 'destino': 'São Paulo', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa B', 'produto': 'Torradeira', 'origem': 'Unidade 2', 'destino': 'Osasco', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa B', 'produto': 'Torradeira', 'origem': 'Unidade 2', 'destino': 'Taboão', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa B', 'produto': 'Torradeira', 'origem': 'Unidade 3', 'destino': 'São Paulo', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa B', 'produto': 'Torradeira', 'origem': 'Unidade 3', 'destino': 'Osasco', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa B', 'produto': 'Torradeira', 'origem': 'Unidade 3', 'destino': 'Taboão', 'custo': Decimal('1.00')},

    # EMPRESA C
    # Cafeteira
    {'empresa': 'Empresa C', 'produto': 'Cafeteira', 'origem': 'Unidade 1', 'destino': 'São Paulo', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa C', 'produto': 'Cafeteira', 'origem': 'Unidade 1', 'destino': 'Osasco', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa C', 'produto': 'Cafeteira', 'origem': 'Unidade 1', 'destino': 'Taboão', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa C', 'produto': 'Cafeteira', 'origem': 'Unidade 2', 'destino': 'São Paulo', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa C', 'produto': 'Cafeteira', 'origem': 'Unidade 2', 'destino': 'Osasco', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa C', 'produto': 'Cafeteira', 'origem': 'Unidade 2', 'destino': 'Taboão', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa C', 'produto': 'Cafeteira', 'origem': 'Unidade 3', 'destino': 'São Paulo', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa C', 'produto': 'Cafeteira', 'origem': 'Unidade 3', 'destino': 'Osasco', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa C', 'produto': 'Cafeteira', 'origem': 'Unidade 3', 'destino': 'Taboão', 'custo': Decimal('1.00')},
    # Torradeira
    {'empresa': 'Empresa C', 'produto': 'Torradeira', 'origem': 'Unidade 1', 'destino': 'São Paulo', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa C', 'produto': 'Torradeira', 'origem': 'Unidade 1', 'destino': 'Osasco', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa C', 'produto': 'Torradeira', 'origem': 'Unidade 1', 'destino': 'Taboão', 'custo': Decimal('3.00')},
    {'empresa': 'Empresa C', 'produto': 'Torradeira', 'origem': 'Unidade 2', 'destino': 'São Paulo', 'custo': Decimal('3.00')},
    {'empresa': 'Empresa C', 'produto': 'Torradeira', 'origem': 'Unidade 2', 'destino': 'Osasco', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa C', 'produto': 'Torradeira', 'origem': 'Unidade 2', 'destino': 'Taboão', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa C', 'produto': 'Torradeira', 'origem': 'Unidade 3', 'destino': 'São Paulo', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa C', 'produto': 'Torradeira', 'origem': 'Unidade 3', 'destino': 'Osasco', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa C', 'produto': 'Torradeira', 'origem': 'Unidade 3', 'destino': 'Taboão', 'custo': Decimal('1.00')},

    # EMPRESA D
    # Cafeteira
    {'empresa': 'Empresa D', 'produto': 'Cafeteira', 'origem': 'Unidade 1', 'destino': 'São Paulo', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa D', 'produto': 'Cafeteira', 'origem': 'Unidade 1', 'destino': 'Osasco', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa D', 'produto': 'Cafeteira', 'origem': 'Unidade 1', 'destino': 'Taboão', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa D', 'produto': 'Cafeteira', 'origem': 'Unidade 2', 'destino': 'São Paulo', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa D', 'produto': 'Cafeteira', 'origem': 'Unidade 2', 'destino': 'Osasco', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa D', 'produto': 'Cafeteira', 'origem': 'Unidade 2', 'destino': 'Taboão', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa D', 'produto': 'Cafeteira', 'origem': 'Unidade 3', 'destino': 'São Paulo', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa D', 'produto': 'Cafeteira', 'origem': 'Unidade 3', 'destino': 'Osasco', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa D', 'produto': 'Cafeteira', 'origem': 'Unidade 3', 'destino': 'Taboão', 'custo': Decimal('1.00')},
    # Torradeira
    {'empresa': 'Empresa D', 'produto': 'Torradeira', 'origem': 'Unidade 1', 'destino': 'São Paulo', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa D', 'produto': 'Torradeira', 'origem': 'Unidade 1', 'destino': 'Osasco', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa D', 'produto': 'Torradeira', 'origem': 'Unidade 1', 'destino': 'Taboão', 'custo': Decimal('3.00')},
    {'empresa': 'Empresa D', 'produto': 'Torradeira', 'origem': 'Unidade 2', 'destino': 'São Paulo', 'custo': Decimal('3.00')},
    {'empresa': 'Empresa D', 'produto': 'Torradeira', 'origem': 'Unidade 2', 'destino': 'Osasco', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa D', 'produto': 'Torradeira', 'origem': 'Unidade 2', 'destino': 'Taboão', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa D', 'produto': 'Torradeira', 'origem': 'Unidade 3', 'destino': 'São Paulo', 'custo': Decimal('2.00')},
    {'empresa': 'Empresa D', 'produto': 'Torradeira', 'origem': 'Unidade 3', 'destino': 'Osasco', 'custo': Decimal('1.00')},
    {'empresa': 'Empresa D', 'produto': 'Torradeira', 'origem': 'Unidade 3', 'destino': 'Taboão', 'custo': Decimal('1.00')},
]
