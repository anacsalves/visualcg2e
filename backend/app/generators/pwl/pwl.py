#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import random
import networkx as nx
from .constants import (
    TIPOS_DIRIGIDOS, TIPOS_MULTIGRAFOS, TIPOS_PSEUDOGRAFOS,
    GRAU_MIN_PADRAO, GAMMA_MIN, GAMMA_MAX
)


def gerarGrausZipf(n, gamma, kMin=GRAU_MIN_PADRAO, kMax=None):
    """
    Gera uma lista de graus seguindo distribuição Zipf (power-law).
    
    A distribuição Zipf é uma forma específica de power-law onde a probabilidade
    de um grau k é proporcional a k^(-gamma). Esta implementação garante que
    todos os graus gerados estejam dentro dos limites especificados.
    
    Args:
        n (int): Número de vértices (tamanho da lista de graus)
        gamma (float): Expoente da distribuição power-law (tipicamente 2.0-3.0)
        kMin (int): Grau mínimo permitido (padrão: GRAU_MIN_PADRAO)
        kMax (int): Grau máximo permitido (padrão: n-1)
    
    Returns:
        list: Lista de n graus seguindo distribuição Zipf
        
    Note:
        - gamma > 1 para que a distribuição seja bem definida
        - kMin deve ser >= 1 para grafos válidos
        - kMax deve ser <= n-1 para grafos simples
        
    Example:
        >>> gerarGrausZipf(100, 2.5)
        [3, 1, 2, 1, 4, 1, 2, 1, 1, ...]  # 100 graus com gamma=2.5
    """
    if kMax is None:
        kMax = n - 1
    
    graus = []
    tentativas_max = n * 10  # Evita loop infinito em casos extremos
    tentativas = 0
    
    while len(graus) < n and tentativas < tentativas_max:
        k = np.random.zipf(gamma)
        if kMin <= k <= kMax:
            graus.append(k)
        tentativas += 1
    
    # Se não conseguiu gerar suficientes, completa com grau mínimo
    while len(graus) < n:
        graus.append(kMin)
    
    return graus


def geraGrausPwl(n, gamma, kMin=GRAU_MIN_PADRAO, kMax=None, desequilibrado=False):
    """Gera graus para grafos power-law, com opção de graus desequilibrados para grafos dirigidos."""
    if desequilibrado:
        graus_out = gerarGrausZipf(n, gamma, kMin, kMax)
        graus_in = gerarGrausZipf(n, gamma, kMin, kMax)
        return graus_out, graus_in
    else:
        return gerarGrausZipf(n, gamma, kMin, kMax)


def ajustaGrausDirigidos(graus_out, graus_in):
    """
    Ajusta graus de entrada e saída para que tenham a mesma soma.
    
    Para grafos dirigidos válidos, a soma dos graus de saída deve ser igual
    à soma dos graus de entrada. Esta função ajusta os graus adicionando
    unidades aleatoriamente até que as somas sejam iguais.
    
    Args:
        graus_out (list): Lista de graus de saída dos vértices
        graus_in (list): Lista de graus de entrada dos vértices
    
    Returns:
        tuple: (graus_out_ajustado, graus_in_ajustado) com somas iguais
        
    Note:
        - Modifica as listas in-place para eficiência
        - Mantém a distribuição power-law aproximada
        - Escolhe vértices aleatoriamente para ajuste
        
    Example:
        >>> graus_out = [3, 2, 4, 1]  # soma = 10
        >>> graus_in = [2, 3, 2, 2]   # soma = 9
        >>> ajustaGrausDirigidos(graus_out, graus_in)
        ([3, 2, 4, 1], [2, 3, 2, 3])  # ambas somam 10
    """
    soma_out = sum(graus_out)
    soma_in = sum(graus_in)
    diff = soma_out - soma_in

    if diff != 0:
        # Determina qual lista precisa ser ajustada
        target = graus_in if diff > 0 else graus_out
        abs_diff = abs(diff)
        
        # Escolhe vértices aleatoriamente para adicionar graus
        indices = np.random.choice(len(target), abs_diff, replace=True)
        for idx in indices:
            target[idx] += 1
    
    return graus_out, graus_in


def constroiGrafoDirigido(graus, tipo, n):
    """
    Constrói grafo dirigido usando algoritmo de stub matching.
    
    O stub matching é um algoritmo clássico para gerar grafos com sequência
    de graus específica. Funciona criando "stubs" (pontas de arestas) para
    cada vértice e conectando-os aleatoriamente.
    
    Args:
        graus: Lista de graus ou tupla (graus_out, graus_in) para grafos dirigidos
        tipo (int): Tipo do grafo (determina se é multigrafo/pseudografo)
        n (int): Número de vértices
    
    Returns:
        nx.DiGraph or nx.MultiDiGraph: Grafo dirigido construído
        
    Algorithm:
        1. Cria stubs de saída e entrada baseado nos graus
        2. Embaralha os stubs aleatoriamente
        3. Conecta stubs de saída com stubs de entrada
        4. Respeita restrições de laços e arestas múltiplas
        
    Example:
        >>> graus = ([3, 2, 1], [2, 2, 2])  # graus out/in
        >>> G = constroiGrafoDirigido(graus, 1, 3)
        >>> G.number_of_edges()
        6  # soma dos graus de saída
    """
    multigrafo = tipo in TIPOS_MULTIGRAFOS
    laco = tipo in TIPOS_PSEUDOGRAFOS
    
    # Cria grafo apropriado baseado no tipo
    G = nx.MultiDiGraph() if multigrafo else nx.DiGraph()
    G.add_nodes_from(range(n))

    # Processa graus (pode ser lista única ou tupla para dirigidos)
    if isinstance(graus, tuple):
        graus_out, graus_in = graus
    else:
        graus_out = graus_in = graus

    # Passo 1: Ajusta graus para garantir soma igual
    graus_out, graus_in = ajustaGrausDirigidos(graus_out, graus_in)

    # Passo 2: Cria stubs (pontas de arestas)
    out_stubs, in_stubs = [], []
    for node, k in enumerate(graus_out):
        out_stubs.extend([node] * k)  # k stubs de saída para o vértice
    for node, k in enumerate(graus_in):
        in_stubs.extend([node] * k)   # k stubs de entrada para o vértice

    # Passo 3: Embaralha stubs para randomização
    random.shuffle(out_stubs)
    random.shuffle(in_stubs)

    # Passo 4: Conecta stubs respeitando restrições
    while out_stubs and in_stubs:
        u = out_stubs.pop()  # Vértice de origem
        v = in_stubs.pop()   # Vértice de destino
        
        # Evita laços se não permitido
        if not laco and u == v:
            continue
        # Evita arestas múltiplas se não permitido
        if not multigrafo and G.has_edge(u, v):
            continue
            
        G.add_edge(u, v)

    return G


def constroiGrafoNaoDirigido(graus, tipo, n):
    """Constrói grafo não dirigido usando stub matching."""
    multigrafo = tipo in TIPOS_MULTIGRAFOS
    laco = tipo in TIPOS_PSEUDOGRAFOS
    
    G = nx.MultiGraph() if multigrafo else nx.Graph()
    G.add_nodes_from(range(n))

    # Cria stubs
    stubs = []
    for node, grau in enumerate(graus):
        stubs.extend([node] * grau)
    random.shuffle(stubs)

    # Conecta stubs
    while len(stubs) > 1:
        u = stubs.pop()
        v = stubs.pop()
        if not laco and u == v:
            continue
        if not multigrafo and G.has_edge(u, v):
            continue
        G.add_edge(u, v)

    return G


def adicionaCaracteristicasEspeciais(G, tipo):
    """Adiciona características especiais como multigrafos e laços."""
    multigrafo = tipo in TIPOS_MULTIGRAFOS
    laco = tipo in TIPOS_PSEUDOGRAFOS

    # Garante que multigrafos tenham pelo menos uma aresta múltipla
    if multigrafo:
        edges = list(G.edges())
        if edges:
            u, v = edges[0]
            G.add_edge(u, v)

    # Garante que pseudografos tenham pelo menos um laço
    if laco and not any(u == v for u, v in G.edges()):
        v = random.choice(list(G.nodes()))
        G.add_edge(v, v)

    return G


def constroiGrafo(graus, tipo):
    """Constrói grafo baseado no tipo especificado."""
    n = len(graus) if isinstance(graus, list) else len(graus[0])
    dirigido = tipo in TIPOS_DIRIGIDOS

    if dirigido:
        G = constroiGrafoDirigido(graus, tipo, n)
    else:
        G = constroiGrafoNaoDirigido(graus, tipo, n)

    G = adicionaCaracteristicasEspeciais(G, tipo)
    return G


def geraGrafoPwl(numV, gamma=2.5, dirigido=False, tipo=0, seed=None, desequilibrado=False):
    """Função principal para gerar grafos power-law."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    graus = geraGrausPwl(numV, gamma, desequilibrado=desequilibrado)
    G = constroiGrafo(graus, tipo)

    if dirigido:
        numA = G.number_of_edges()
        graus_out = graus[0] if isinstance(graus, tuple) else graus
        graus_resultado = graus_out
    else:
        numA = sum(dict(G.degree()).values()) // 2
        graus_resultado = graus

    arestas = list(G.edges())[:numA]
    return arestas, G, graus_resultado


def tipoGrafo(G):
    """Detecta automaticamente o tipo do grafo."""
    dirigido = G.is_directed()
    multigrafo = G.is_multigraph()
    laco = any(u == v for u, v in G.edges())
    multipla = any(G.number_of_edges(u, v) > 1 for u, v in G.edges()) if multigrafo else False

    if dirigido and multipla and laco:
        return 31
    elif dirigido and multipla:
        return 21
    elif dirigido:
        return 1
    elif laco:
        return 30
    elif multipla:
        return 20
    else:
        return 0
