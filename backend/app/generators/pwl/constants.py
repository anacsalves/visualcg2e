#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constantes compartilhadas para o módulo powerlaw.

Este módulo centraliza todas as constantes utilizadas pelo sistema de geração
de grafos com distribuição power-law, facilitando manutenção e garantindo
consistência entre diferentes partes do código.
"""

# =============================================================================
# TIPOS DE GRAFOS SUPORTADOS
# =============================================================================

# Mapeamento completo de tipos de grafos
TIPOS_GRAFOS = {
    0: 'Simples',           # Não dirigido, sem laços, sem arestas múltiplas
    1: 'Digrafo',           # Dirigido, sem laços, sem arestas múltiplas
    20: 'Multigrafo',       # Não dirigido, sem laços, com arestas múltiplas
    21: 'Multigrafo-Dirigido', # Dirigido, sem laços, com arestas múltiplas
    30: 'Pseudografo',      # Não dirigido, com laços, com arestas múltiplas
    31: 'Pseudografo-Dirigido'  # Dirigido, com laços, com arestas múltiplas
}

# Agrupamentos por características
TIPOS_DIRIGIDOS = [1, 21, 31]      # Grafos com arestas direcionadas
TIPOS_MULTIGRAFOS = [20, 21, 30, 31]  # Grafos que permitem arestas múltiplas
TIPOS_PSEUDOGRAFOS = [30, 31]      # Grafos que permitem laços

# =============================================================================
# PARÂMETROS POWER-LAW
# =============================================================================

# Limites para o expoente gamma da distribuição power-law
GAMMA_MIN = 2.0    # Expoente mínimo (grafos mais densos)
GAMMA_MAX = 3.0    # Expoente máximo (grafos mais esparsos)

# Parâmetros de grau
GRAU_MIN_PADRAO = 1    # Grau mínimo para qualquer vértice

# Parâmetros para análise power-law
XMIN_POWERLAW = 2      # Valor mínimo para ajuste da distribuição power-law
KS_THRESHOLD = 0.1     # Limite para teste Kolmogorov-Smirnov (p-value)

# =============================================================================
# CONFIGURAÇÕES DE TESTE
# =============================================================================

# Configurações padrão para execução de testes
NUM_EXECUCOES_PADRAO = 5    # Número padrão de execuções por configuração
VERTICES_LISTA_PADRAO = [1000, 5000]  # Tamanhos padrão de vértices para testes
MAX_AMOSTRAS_HOP = 10000    # Máximo de amostras para cálculo de distâncias

# =============================================================================
# CONFIGURAÇÕES DE VISUALIZAÇÃO
# =============================================================================

# Limites para visualização de grafos
MAX_NOS_VISUALIZACAO = 300  # Máximo de nós para visualização completa
TAMANHO_NOS_PEQUENOS = 100  # Tamanho para considerar grafo "pequeno" 