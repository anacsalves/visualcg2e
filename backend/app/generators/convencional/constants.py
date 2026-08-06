#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constantes compartilhadas para o módulo simples.

Este módulo centraliza todas as constantes utilizadas pelo sistema de geração
de grafos, facilitando manutenção e garantindo consistência entre diferentes
partes do código.
"""

# =============================================================================
# TIPOS DE GRAFOS SUPORTADOS
# =============================================================================

# Mapeamento completo de tipos de grafos
TIPOS_GRAFOS = {
    0: "Simples",           # Não dirigido, sem laços, sem arestas múltiplas
    1: "Digrafo",           # Dirigido, sem laços, sem arestas múltiplas
    20: "Multigrafo",       # Não dirigido, sem laços, com arestas múltiplas
    21: "Multigrafo-Dirigido", # Dirigido, sem laços, com arestas múltiplas
    30: "Pseudografo",      # Não dirigido, com laços, com arestas múltiplas
    31: "Pseudografo-Dirigido", # Dirigido, com laços, com arestas múltiplas
}

# Lista de tipos válidos para uso em loops
TIPOS_VALIDOS = [0, 1, 20, 21, 30, 31]

# Agrupamentos por características
TIPOS_DIRIGIDOS = [1, 21, 31]      # Grafos com arestas direcionadas
TIPOS_MULTIGRAFOS = [20, 21, 30, 31]  # Grafos que permitem arestas múltiplas
TIPOS_PSEUDOGRAFOS = [30, 31]      # Grafos que permitem laços
TIPOS_SIMPLES = [0, 20, 30]        # Grafos não dirigidos

# =============================================================================
# ESTRATÉGIAS DE GERAÇÃO
# =============================================================================

# Estratégias para alocação de vértices e arestas
GERACAO = {
    0: "Aleatório",              # Distribuição completamente aleatória
    1: "Parcialmente Balanceado", # Distribuição semi-aleatória com ordenação
    2: "Balanceado"              # Distribuição o mais uniforme possível
}

# Preferências de densidade do grafo
DENSIDADE = {
    0: "Sem preferência",        # Aceita qualquer densidade
    1: "Esparso (densidade ≤ 0.2)", # Prefere grafos esparsos
    2: "Denso (densidade ≥ 0.8)"    # Prefere grafos densos
}

# =============================================================================
# PARÂMETROS PADRÃO
# =============================================================================

# Limites de tentativas e amostras
MAX_TENTATIVAS = 1000       # Máximo de tentativas para gerar grafo válido
MAX_AMOSTRAS_HOP = 10000    # Máximo de amostras para cálculo de distâncias

# Pesos padrão para grafos valorados
PESO_MIN_PADRAO = 1         # Peso mínimo das arestas
PESO_MAX_PADRAO = 10        # Peso máximo das arestas

# =============================================================================
# CONFIGURAÇÕES DE TESTE
# =============================================================================

# Configurações padrão para execução de testes
NUM_EXECUCOES_PADRAO = 5    # Número padrão de execuções por configuração
VERTICES_LISTA_PADRAO = [100, 500]  # Tamanhos padrão de vértices para testes (demonstração)

# =============================================================================
# CONFIGURAÇÕES DE DENSIDADE
# =============================================================================

# Limites para classificação de densidade
DENSIDADE_ESPARSA_MAX = 0.2  # Máximo para considerar grafo esparso
DENSIDADE_DENSA_MIN = 0.8    # Mínimo para considerar grafo denso 