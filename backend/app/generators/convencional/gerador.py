#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import math
import numpy as np
import time
from .constants import (
    TIPOS_DIRIGIDOS, TIPOS_MULTIGRAFOS, TIPOS_PSEUDOGRAFOS,
    MAX_TENTATIVAS
)
from .exceptions import (
    ParametrosInvalidosError, TentativasExcedidasError,
    ArestasInsuficientesError, ComponentesInvalidasError
)
from .utils import tipoGrafo, compConexas


def verificaAresta(tipo, numV, numC):
    """
    Verifica se os parâmetros de arestas são válidos para o tipo de grafo especificado.
    
    Calcula os limites mínimo e máximo de arestas baseado no tipo de grafo:
    - Simples (0): Arestas únicas, sem laços
    - Digrafo (1): Arestas direcionadas
    - Multigrafo (20/21): Arestas múltiplas permitidas
    - Pseudografo (30/31): Laços permitidos
    
    Args:
        tipo (int): Tipo do grafo (0, 1, 20, 21, 30, 31)
        numV (int): Número de vértices
        numC (int): Número de componentes conexas
    
    Returns:
        tuple: (minimo, maximo) - Limites de arestas válidas
        
    Raises:
        ComponentesInvalidasError: Se numV < numC
        ParametrosInvalidosError: Se tipo de grafo é inválido
    
    Example:
        >>> verificaAresta(0, 10, 2)
        (7, 28)  # Para grafo simples com 10 vértices e 2 componentes
    """
    # Validação básica: deve ter vértices suficientes para as componentes
    if numV - (numC - 1) <= 0:
        raise ComponentesInvalidasError(
            f"Número de vértices ({numV}) insuficiente para {numC} componentes conexas"
        )

    # Vértices efetivos (considerando componentes)
    vertices_efetivos = numV - (numC - 1)
    
    # Estratégia baseada no tipo de grafo
    if tipo == 0:  # Simples: sem laços, sem arestas múltiplas
        minimo = vertices_efetivos - 1  # Árvore mínima
        maximo = (vertices_efetivos * (vertices_efetivos - 1)) / 2  # Grafo completo
    elif tipo == 1:  # Digrafo: direcionado, sem laços
        minimo = vertices_efetivos - 1  # Árvore direcionada mínima
        maximo = vertices_efetivos * (vertices_efetivos - 1)  # Grafo direcionado completo
    elif "2" in str(tipo):  # Multigrafo: arestas múltiplas permitidas
        minimo = vertices_efetivos  # Mínimo para garantir conectividade
        maximo = math.inf  # Sem limite superior
    elif "3" in str(tipo):  # Pseudografo: laços permitidos
        minimo = vertices_efetivos  # Mínimo para garantir conectividade
        maximo = math.inf  # Sem limite superior
    else:
        raise ParametrosInvalidosError(f"Tipo de grafo inválido: {tipo}")
    
    return minimo, maximo


def alocaVertices(numV, numC, fator):
    """
    Aloca vértices para componentes conexas baseado na estratégia especificada.
    
    Estratégias de alocação:
    - fator = 0: Aleatório - Distribuição uniforme aleatória
    - fator = 1: Parcialmente Balanceado - Distribuição semi-aleatória
    - fator = 2: Balanceado - Distribuição o mais uniforme possível
    
    Args:
        numV (int): Número total de vértices
        numC (int): Número de componentes conexas
        fator (int): Estratégia de alocação (0, 1, ou 2)
    
    Returns:
        list: Lista com número de vértices por componente
        
    Example:
        >>> alocaVertices(10, 3, 2)
        [4, 3, 3]  # Distribuição balanceada
        >>> alocaVertices(10, 3, 0)
        [3, 4, 3]  # Distribuição aleatória
    """
    verticesComp = [0] * numC
    
    if fator == 2:  # Balanceado: distribuição o mais uniforme possível
        resto = numV % numC
        vert = numV // numC
        verticesComp = [vert] * numC
        # Adiciona o resto na primeira componente para manter balanceamento
        verticesComp[0] += resto
    else:  # Aleatório (fator=0) ou Parcialmente Balanceado (fator=1)
        for _ in range(numV):
            component = random.randint(0, numC - 1)
            verticesComp[component] += 1
    
    return verticesComp


def calculaLimitesArestas(verticesComp, tipo):
    """Calcula limites mínimo e máximo de arestas para cada componente."""
    minArestas = [0] * len(verticesComp)
    maxArestas = [0] * len(verticesComp)
    
    for i, numVertices in enumerate(verticesComp):
        if tipo == 0:  # Simples
            minArestas[i] = numVertices - 1
            maxArestas[i] = (numVertices * (numVertices - 1)) / 2
        elif tipo == 1:  # Dirigido
            minArestas[i] = numVertices - 1
            maxArestas[i] = numVertices * (numVertices - 1)
        elif "2" in str(tipo):  # Multigrafo
            if numVertices == 1:
                minArestas[i] = 0
                maxArestas[i] = 0
            else:
                minArestas[i] = numVertices
                maxArestas[i] = math.inf
        elif "3" in str(tipo):  # Pseudografo
            minArestas[i] = numVertices
            maxArestas[i] = math.inf
    
    return minArestas, maxArestas


def alocaArestasBalanceado(numA, numC, minArestas, maxArestas):
    """Aloca arestas de forma balanceada entre componentes."""
    resto = numA % numC
    arest = numA // numC
    arestasComp = [arest] * numC
    arestasComp[0] += resto
    
    # Valida se é possível
    for i in range(numC):
        if minArestas[i] > arestasComp[i]:
            raise ArestasInsuficientesError(
                "Não é possível gerar um grafo balanceado com esse número de arestas, considere aumentar"
            )
        elif maxArestas[i] < arestasComp[i]:
            raise ArestasInsuficientesError(
                "Não é possível gerar um grafo balanceado com esse número de arestas, considere diminuir"
            )
    
    return arestasComp


def alocaArestasAleatorio(numA, numC, minArestas, maxArestas):
    """Aloca arestas de forma aleatória entre componentes."""
    arestasComp = [0] * numC
    arestasRestantes = numA
    
    for i in range(numC - 1):
        if minArestas[i] < maxArestas[i]:
            try:
                max_possivel = min(
                    maxArestas[i],
                    arestasRestantes - sum(
                        min(minArestas[j], maxArestas[j])
                        for j in range(i + 1, numC)
                    )
                )
                arestasComp[i] = random.randint(minArestas[i], int(max_possivel))
            except ValueError as e:
                raise ArestasInsuficientesError(
                    f"Erro ao gerar valor aleatório para arestasComp[{i}]: {e}"
                )
        arestasRestantes -= arestasComp[i]
    
    # Última componente recebe o restante
    arestasComp[numC - 1] = numA - sum(arestasComp)
    
    # Valida última componente
    if (arestasComp[numC - 1] < minArestas[numC - 1] or 
        arestasComp[numC - 1] > maxArestas[numC - 1]):
        return None  # Indica que deve tentar novamente
    
    return arestasComp


def constroiComponentes(verticesComp, arestasComp, tipo, numV):
    """Constrói as componentes do grafo."""
    numC = len(verticesComp)
    
    # Calcula tamanhos acumulados
    tam = [0] * (numC + 1)
    for j in range(1, numC):
        tam[j] = tam[j - 1] + verticesComp[j - 1]
    tam[numC] = numV
    
    # Constrói matriz de adjacência
    matriz = np.array([[0] * numV for _ in range(numV)])
    arestas = []
    
    for i in range(numC):
        # Lista de vértices da componente atual
        vertices = list(range(tam[i], tam[i + 1]))
        random.shuffle(vertices)
        
        # Conecta vértices da componente
        for j in range(len(vertices) - 1):
            u, v = vertices[j], vertices[j + 1]
            if tipo in [0, 20, 30]:  # Grafo não dirigido
                arestas.append((u, v))
                if tipo == 0:  # Simples: máximo 1 aresta
                    matriz[u][v] = 1
                    matriz[v][u] = 1
                else:  # Multigrafo/Pseudografo: pode ter múltiplas
                    matriz[u][v] += 1
                    matriz[v][u] += 1
            else:  # Grafo dirigido
                arestas.append((u, v))
                if tipo == 1:  # Digrafo: máximo 1 aresta
                    matriz[u][v] = 1
                else:  # Multigrafo-Dirigido/Pseudografo-Dirigido: pode ter múltiplas
                    matriz[u][v] += 1
        
        # Adiciona arestas extras se necessário
        arestas_necessarias = arestasComp[i] - (len(vertices) - 1)
        tentativas_aresta = 0
        arestas_adicionadas = 0
        
        # Para pseudografos, garante pelo menos alguns loops
        loops_adicionados = 0
        if tipo in TIPOS_PSEUDOGRAFOS:
            num_loops = min(arestas_necessarias // 3, len(vertices) // 2)  # 1/3 das arestas ou metade dos vértices
            for _ in range(num_loops):
                u = random.choice(vertices)
                if tipo in [0, 20, 30]:  # Grafo não dirigido
                    arestas.append((u, u))
                    matriz[u][u] += 1
                else:  # Grafo dirigido
                    arestas.append((u, u))
                    matriz[u][u] += 1
                loops_adicionados += 1
            arestas_necessarias -= loops_adicionados
        
        # Limite proporcional ao número de arestas necessárias
        limite_tentativas = MAX_TENTATIVAS * max(1, arestas_necessarias)
        while arestas_adicionadas < arestas_necessarias and tentativas_aresta < limite_tentativas:
            u = random.choice(vertices)
            v = random.choice(vertices)
            tentativas_aresta += 1
            
            # Verifica se a aresta é válida
            if u != v or tipo in TIPOS_PSEUDOGRAFOS:
                if tipo in [0, 20, 30]:  # Grafo não dirigido
                    # Para grafos simples, verifica se a aresta já existe
                    if tipo == 0 and matriz[u][v] > 0:
                        continue  # Aresta já existe, tenta outra
                    
                    arestas.append((min(u, v), max(u, v)))
                    if tipo == 0:  # Simples: máximo 1 aresta
                        matriz[u][v] = 1
                        matriz[v][u] = 1
                    else:  # Multigrafo/Pseudografo: pode ter múltiplas
                        matriz[u][v] += 1
                        matriz[v][u] += 1
                    arestas_adicionadas += 1
                else:  # Grafo dirigido
                    # Para digrafos, verifica se a aresta já existe
                    if tipo == 1 and matriz[u][v] > 0:
                        continue  # Aresta já existe, tenta outra
                    
                    arestas.append((u, v))
                    if tipo == 1:  # Digrafo: máximo 1 aresta
                        matriz[u][v] = 1
                    else:  # Multigrafo-Dirigido/Pseudografo-Dirigido: pode ter múltiplas
                        matriz[u][v] += 1
                    arestas_adicionadas += 1
    
    # Verificação final: garante que pseudografos tenham loops
    if tipo in TIPOS_PSEUDOGRAFOS:
        # Verifica se há loops na matriz
        tem_loops = False
        for i in range(numV):
            if matriz[i][i] > 0:
                tem_loops = True
                break
        
        # Se não há loops, adiciona pelo menos um
        if not tem_loops:
            u = random.choice(range(numV))
            arestas.append((u, u))
            matriz[u][u] += 1
    
    # Verificação final: garante que multigrafos tenham arestas múltiplas
    if tipo in TIPOS_MULTIGRAFOS and tipo not in TIPOS_PSEUDOGRAFOS:
        # Verifica se há arestas múltiplas na matriz
        tem_multiplas = False
        for i in range(numV):
            for j in range(numV):
                if matriz[i][j] > 1:
                    tem_multiplas = True
                    break
            if tem_multiplas:
                break
        
        # Se não há arestas múltiplas, adiciona pelo menos uma
        if not tem_multiplas:
            u = random.choice(range(numV))
            v = random.choice(range(numV))
            if u != v:  # Não adiciona loop para multigrafos não-pseudografos
                arestas.append((min(u, v), max(u, v)) if tipo in [0, 20, 30] else (u, v))
                matriz[u][v] += 1
                if tipo in [0, 20, 30]:  # Grafo não dirigido
                    matriz[v][u] += 1
    
    return arestas


def geraComponente(tipo, numV, numA, numC, fator):
    """
    Gera um grafo com múltiplas componentes conexas.
    
    Esta função implementa o algoritmo principal de geração de grafos com componentes
    conexas. Utiliza uma abordagem de tentativa e erro com validação rigorosa.
    
    Algoritmo:
    1. Aloca vértices para componentes baseado na estratégia
    2. Calcula limites válidos de arestas para cada componente
    3. Aloca arestas respeitando os limites calculados
    4. Constrói as componentes usando stub matching
    5. Repete em caso de falha até MAX_TENTATIVAS
    
    Args:
        tipo (int): Tipo do grafo (0, 1, 20, 21, 30, 31)
        numV (int): Número total de vértices
        numA (int): Número total de arestas
        numC (int): Número de componentes conexas
        fator (int): Estratégia de alocação (0=aleatório, 1=parcial, 2=balanceado)
    
    Returns:
        list: Lista de tuplas (u, v) representando as arestas do grafo
        
    Raises:
        TentativasExcedidasError: Se não conseguir gerar após MAX_TENTATIVAS
        ArestasInsuficientesError: Se parâmetros de arestas são inválidos
        ComponentesInvalidasError: Se configuração de componentes é inválida
        
    Example:
        >>> geraComponente(0, 10, 15, 2, 2)
        [(0, 1), (1, 2), (2, 3), (4, 5), ...]  # Grafo simples com 2 componentes
    """
    tentativas = 0
    
    while tentativas < MAX_TENTATIVAS:
        # Passo 1: Aloca vértices para componentes baseado na estratégia
        verticesComp = alocaVertices(numV, numC, fator)
        if not all(verticesComp):  # Valida se todas as componentes têm vértices
            tentativas += 1
            continue
        
        # Passo 2: Calcula limites válidos de arestas para cada componente
        minArestas, maxArestas = calculaLimitesArestas(verticesComp, tipo)
        
        # Passo 3: Aloca arestas respeitando os limites calculados
        if fator == 2:  # Balanceado: distribuição uniforme
            try:
                arestasComp = alocaArestasBalanceado(numA, numC, minArestas, maxArestas)
            except ArestasInsuficientesError:
                tentativas += 1
                continue
        else:  # Aleatório ou Parcialmente Balanceado
            arestasComp = alocaArestasAleatorio(numA, numC, minArestas, maxArestas)
            if arestasComp is None:  # Falha na alocação
                tentativas += 1
                continue
        
        # Passo 4: Ordena se parcialmente balanceado para consistência
        if fator == 1:
            verticesComp = sorted(verticesComp)
            arestasComp = sorted(arestasComp)
        
        # Passo 5: Constrói as componentes usando stub matching
        try:
            arestas = constroiComponentes(verticesComp, arestasComp, tipo, numV)
            # Validação: verifica se número de arestas geradas corresponde ao solicitado
            if len(arestas) != numA:
                tentativas += 1
                continue
            return arestas
        except Exception:  # Falha na construção
            tentativas += 1
            continue
    
    return None


def geraGrafoSimples(numV, numA):
    """Gera grafo simples com otimização para grafos densos."""
    max_arestas = numV * (numV - 1) // 2
    if numA > max_arestas:
        raise ArestasInsuficientesError(
            "Número de arestas excede o máximo permitido para um grafo simples."
        )
    
    # Para grafos muito densos (>80% da densidade máxima), usa algoritmo determinístico
    densidade = numA / max_arestas if max_arestas > 0 else 0
    if densidade > 0.8:
        # Algoritmo determinístico para grafos densos (evita travamentos)
        arestas = []
        for u in range(numV):
            for v in range(u + 1, numV):
                if len(arestas) >= numA:
                    break
                arestas.append((u, v))
            if len(arestas) >= numA:
                break
        return arestas[:numA]
    
    # Algoritmo aleatório para grafos esparsos (comportamento normal)
    arestas_set = set()
    tentativas = 0
    limite = MAX_TENTATIVAS * max(1, numA)
    while len(arestas_set) < numA and tentativas < limite:
        u = random.randint(0, numV - 1)
        v = random.randint(0, numV - 1)
        tentativas += 1
        if u != v:
            aresta = (u, v) if u < v else (v, u)
            if aresta not in arestas_set:
                arestas_set.add(aresta)
    
    return list(arestas_set)


def geraGrafoDirigido(numV, numA):
    """Gera grafo dirigido."""
    if numA > numV * (numV - 1):
        raise ArestasInsuficientesError(
            "Número de arestas excede o máximo permitido para um digrafo."
        )
    
    arestas_set = set()
    tentativas = 0
    limite = MAX_TENTATIVAS * max(1, numA)
    while len(arestas_set) < numA and tentativas < limite:
        u = random.randint(0, numV - 1)
        v = random.randint(0, numV - 1)
        tentativas += 1
        if u != v:
            aresta = (u, v)
            if aresta not in arestas_set:
                arestas_set.add(aresta)
    
    return list(arestas_set)


def geraMultigrafo(numV, numA, dirigido=False):
    """Gera multigrafo simples ou dirigido."""
    arestas = []
    
    # Gera arestas normais
    while len(arestas) < numA - 1:
        u = random.randint(0, numV - 1)
        v = random.randint(0, numV - 1)
        if u != v:
            if dirigido:
                aresta = (u, v)
            else:
                aresta = (min(u, v), max(u, v))
            arestas.append(aresta)
    
    # Garante que há pelo menos uma aresta múltipla
    if len(set(arestas)) == len(arestas):
        aresta_existente = random.choice(arestas)
        arestas.append(aresta_existente)
    
    return arestas


def geraPseudografo(numV, numA, dirigido=False):
    """Gera pseudografo simples ou dirigido."""
    arestas = []
    loop = False
    
    # Gera arestas normais
    while len(arestas) < numA - 1:
        u = random.randint(0, numV - 1)
        v = random.randint(0, numV - 1)
        if dirigido:
            aresta = (u, v)
        else:
            aresta = (min(u, v), max(u, v))
        arestas.append(aresta)
        if u == v:
            loop = True
    
    # Garante que há pelo menos um laço
    if not loop:
        u = random.randint(0, numV - 1)
        arestas.append((u, u))
    
    return arestas


def geraDataset(tipo, numV, numA, seed, n, numC, fator, medir_tempo=False):
    """Função principal para gerar datasets de grafos."""
    random.seed(seed)
    datasets = []
    
    if numC > 1:
        # Geração com múltiplas componentes
        tentativas = 0
        while len(datasets) != n and tentativas < MAX_TENTATIVAS:
            tentativas += 1
            t0 = time.perf_counter()
            grafo = geraComponente(tipo, numV, numA, numC, fator)
            if grafo is not None:
                tempo_s = time.perf_counter() - t0
                if medir_tempo:
                    datasets.append((sorted(list(grafo)), tempo_s))
                else:
                    datasets.append(sorted(list(grafo)))
                tentativas = 0
            else:
                continue
        
        if tentativas >= MAX_TENTATIVAS:
            raise TentativasExcedidasError(
                "Número máximo de tentativas atingido. Considere alterar parâmetros."
            )
    else:
        # Geração de grafo conexo
        for _ in range(n):
            if tipo == 0:
                t0 = time.perf_counter()
                arestas = geraGrafoSimples(numV, numA)
            elif tipo == 1:
                t0 = time.perf_counter()
                arestas = geraGrafoDirigido(numV, numA)
            elif tipo == 20:
                t0 = time.perf_counter()
                arestas = geraMultigrafo(numV, numA, dirigido=False)
            elif tipo == 21:
                t0 = time.perf_counter()
                arestas = geraMultigrafo(numV, numA, dirigido=True)
            elif tipo == 30:
                t0 = time.perf_counter()
                arestas = geraPseudografo(numV, numA, dirigido=False)
            elif tipo == 31:
                t0 = time.perf_counter()
                arestas = geraPseudografo(numV, numA, dirigido=True)
            else:
                raise ParametrosInvalidosError(f"Tipo de grafo inválido: {tipo}")
            
            tempo_s = time.perf_counter() - t0
            if medir_tempo:
                datasets.append((sorted(list(arestas)), tempo_s))
            else:
                datasets.append(sorted(list(arestas)))
    
    return datasets