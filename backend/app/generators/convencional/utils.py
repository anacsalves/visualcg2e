#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import random



def dfs(matriz, inicio, visitados):
    """
    Implementa busca em profundidade (DFS) para detectar conectividade.
    
    Esta função percorre o grafo a partir de um vértice inicial usando DFS
    iterativo (com pilha) para marcar todos os vértices alcançáveis.
    
    Args:
        matriz: Matriz de adjacências do grafo
        inicio (int): Vértice inicial para iniciar a busca
        visitados (set): Conjunto de vértices já visitados (modificado in-place)
    
    Algorithm:
        - Usa pilha para implementação iterativa (mais eficiente para grafos grandes)
        - Suporta tanto grafos simples quanto multigrafos/pseudografos
        - Marca vértices como visitados durante a busca
        
    Note:
        - Modifica o conjunto visitados in-place
        - Detecta arestas tanto em listas (grafos valorados) quanto números
    """
    pilha = [inicio]
    while pilha:
        vertice = pilha.pop()
        if vertice not in visitados:
            visitados.add(vertice)
            # Explora todos os vizinhos do vértice atual
            for vizinho in range(len(matriz)):
                cell = matriz[vertice][vizinho]
                # Verifica se há conexão (suporta diferentes formatos)
                if isinstance(cell, list):
                    cond = len(cell) >= 1  # Lista não vazia = aresta existe
                else:
                    cond = cell >= 1       # Número >= 1 = aresta existe
                if cond and vizinho not in visitados:
                    pilha.append(vizinho)

def compConexas(matriz):
    """
    Calcula o número de componentes conexas em um grafo.
    
    Uma componente conexa é um subgrafo onde todos os vértices são alcançáveis
    entre si. Esta função conta quantas dessas componentes existem no grafo.
    
    Args:
        matriz: Matriz de adjacências do grafo
    
    Returns:
        int: Número de componentes conexas
        
    Algorithm:
        - Inicializa conjunto de vértices visitados
        - Para cada vértice não visitado, executa DFS
        - Cada DFS marca uma componente conexa completa
        - Conta o número de DFSs executados
        
    Complexity:
        - Time: O(V²) onde V é o número de vértices
        - Space: O(V) para o conjunto de visitados
        
    Example:
        >>> matriz = [[0, 1, 0], [1, 0, 0], [0, 0, 0]]
        >>> compConexas(matriz)
        2  # 2 componentes: {0,1} e {2}
    """
    visitados = set()
    componentes = 0
    
    # Para cada vértice não visitado, inicia uma nova busca
    for vertice in range(len(matriz)):
        if vertice not in visitados:
            # DFS marca todos os vértices da componente atual
            dfs(matriz, vertice, visitados)
            componentes += 1
    
    return componentes



def atribuiPesos(matriz, minPeso, maxPeso):
    for i in range(len(matriz)):
        for j in range(len(matriz[i])):
            if matriz[i][j] > 0:
                matriz[i][j] = sum(
                    [random.randint(minPeso, maxPeso) for _ in range(matriz[i][j])]
                )
    return matriz


def tipoGrafo(matriz):
    """
    Detecta automaticamente o tipo de grafo baseado na matriz de adjacências.
    
    Esta função analisa a estrutura da matriz para determinar as características
    do grafo e classifica em um dos 6 tipos suportados.
    
    Características analisadas:
    - Dirigido: Matriz não é simétrica
    - Arestas múltiplas: Valores > 1 na matriz
    - Laços: Valores > 0 na diagonal principal
    
    Args:
        matriz: Matriz de adjacências do grafo
    
    Returns:
        int: Tipo do grafo conforme codificação:
            - 0: Simples (não dirigido, sem laços, sem arestas múltiplas)
            - 1: Digrafo (dirigido, sem laços, sem arestas múltiplas)
            - 20: Multigrafo (não dirigido, sem laços, com arestas múltiplas)
            - 21: Multigrafo-Dirigido (dirigido, sem laços, com arestas múltiplas)
            - 30: Pseudografo (não dirigido, com laços, com arestas múltiplas)
            - 31: Pseudografo-Dirigido (dirigido, com laços, com arestas múltiplas)
    
    Algorithm:
        1. Verifica presença de laços (diagonal principal)
        2. Verifica presença de arestas múltiplas (valores > 1)
        3. Verifica se é dirigido (simetria da matriz)
        4. Classifica baseado nas características encontradas
        
    Example:
        >>> matriz = [[0, 2, 0], [2, 0, 1], [0, 1, 0]]
        >>> tipoGrafo(matriz)
        20  # Multigrafo (aresta múltipla entre 0 e 1)
    """
    laco = False
    multipla = False
    vert = len(matriz)
    
    # Passo 1: Analisa cada célula da matriz
    for i in range(vert):
        for j in range(vert):
            cell = matriz[i][j]
            
            # Verifica se é uma lista (para grafos valorados)
            if isinstance(cell, list):
                if len(cell) > 1:
                    multipla = True  # Múltiplas arestas
                if len(cell) > 0 and i == j:
                    laco = True      # Laço detectado
            # Verifica se é um número (suporta numpy.integer)
            elif isinstance(cell, (int, float, np.integer)):
                if cell > 1:
                    multipla = True  # Múltiplas arestas
                if cell > 0 and i == j:
                    laco = True      # Laço detectado
    
    # Passo 2: Verifica se é dirigido (matriz não simétrica)
    dirigido = not (np.transpose(matriz) == matriz).all()
    
    # Passo 3: Classifica baseado nas características encontradas
    if dirigido and multipla and laco:
        tipo = 31  # Pseudografo-Dirigido
    elif dirigido and multipla:
        tipo = 21  # Multigrafo-Dirigido
    elif dirigido:
        tipo = 1   # Digrafo
    elif laco:
        tipo = 30  # Pseudografo
    elif multipla:
        tipo = 20  # Multigrafo
    else:
        tipo = 0   # Simples
    
    return tipo

def criaListaAdjacencias(matriz):
    n = len(matriz)
    lista = {}
    for u in range(n):
        adj = []
        for v, cell in enumerate(matriz[u]):
            if isinstance(cell, list):
                for peso in cell:
                    adj.append((v, peso))
            else:
                if cell > 0:
                    adj.append((v, cell))
        lista[u] = adj
    return lista


def criaMatrizAdjacencias(arestas, numV, tipo):
    """Cria matriz de adjacências preservando arestas múltiplas e laços."""
    matriz = np.array([[0] * numV for _ in range(numV)])
    
    # Conta as ocorrências de cada aresta
    from collections import defaultdict
    arestas_count = defaultdict(int)
    
    for u, v in arestas:
        arestas_count[(u, v)] += 1
    
    # Aplica as arestas na matriz
    for (u, v), count in arestas_count.items():
        matriz[u][v] = count
        # Para grafos não dirigidos, adiciona na direção oposta
        if tipo in [0, 20, 30] and u != v:
            matriz[v][u] = count
    
    return matriz


def criaMatrizAdjacenciasValorada(arestas, numV, tipo, minPeso, maxPeso):
    matriz = [[[] for _ in range(numV)] for _ in range(numV)]
    for u, v in arestas:
        peso = random.randint(minPeso, maxPeso)
        matriz[u][v].append(peso)
        if tipo in (0, 20, 30) and u != v:
            matriz[v][u].append(peso)
    return matriz


def escreveMatrizParaArquivo(matriz, listaAdj, nomeArq, numV, numA, seed, n):
    with open(nomeArq, "w") as arquivo:
        arquivo.write(f"numV: {numV}, numA: {numA}, seed: {seed}, n: {n}\n")
        for linha in matriz:
            linha_formatada = " ".join(map(str, linha))
            arquivo.write(f"{linha_formatada}\n")
        arquivo.write(f"{matriz}\n")
        for vertice, adjacencias in listaAdj.items():
            arquivo.write(f"{vertice}: {adjacencias}\n")
