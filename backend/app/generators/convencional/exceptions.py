#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exceções personalizadas para o módulo simples.

Este módulo define uma hierarquia de exceções específicas para o sistema
de geração de grafos, permitindo tratamento de erros mais granular e
informações mais detalhadas sobre falhas durante a geração.
"""

class GrafoGenerationError(Exception):
    """
    Exceção base para todos os erros relacionados à geração de grafos.
    
    Esta é a classe pai de todas as exceções específicas do módulo,
    permitindo capturar qualquer erro de geração com um único except.
    
    Example:
        try:
            geraGrafo(tipo, numV, numA)
        except GrafoGenerationError as e:
            print(f"Erro na geração: {e}")
    """
    pass


class ParametrosInvalidosError(GrafoGenerationError):
    """
    Exceção lançada quando os parâmetros de entrada são inválidos.
    
    Situações que causam este erro:
    - Tipo de grafo não suportado
    - Número de vértices <= 0
    - Número de arestas < mínimo necessário
    - Configurações matematicamente impossíveis
    
    Example:
        >>> geraGrafo(999, 10, 5)  # Tipo inválido
        ParametrosInvalidosError: Tipo de grafo inválido: 999
    """
    pass


class TentativasExcedidasError(GrafoGenerationError):
    """
    Exceção lançada quando o algoritmo não consegue gerar o grafo após
    o número máximo de tentativas.
    
    Esta exceção indica que os parâmetros fornecidos podem ser muito
    restritivos ou matematicamente impossíveis de satisfazer.
    
    Situações comuns:
    - Muitas arestas para poucos vértices
    - Configurações de componentes muito restritivas
    - Parâmetros que criam conflitos insolúveis
    
    Example:
        >>> geraGrafo(0, 5, 100)  # Muitas arestas para grafo simples
        TentativasExcedidasError: Número máximo de tentativas (100) atingido
    """
    pass


class ArestasInsuficientesError(GrafoGenerationError):
    """
    Exceção lançada quando o número de arestas é insuficiente para
    gerar um grafo válido com os parâmetros especificados.
    
    Situações que causam este erro:
    - Arestas < mínimo necessário para conectividade
    - Arestas insuficientes para o número de componentes
    - Configurações que violam restrições do tipo de grafo
    
    Example:
        >>> geraGrafo(0, 10, 5)  # Poucas arestas para 10 vértices
        ArestasInsuficientesError: Mínimo de 9 arestas necessário
    """
    pass


class ComponentesInvalidasError(GrafoGenerationError):
    """
    Exceção lançada quando a configuração de componentes conexas
    é matematicamente impossível ou inválida.
    
    Situações que causam este erro:
    - Número de componentes > número de vértices
    - Vértices insuficientes para as componentes especificadas
    - Configurações que violam propriedades de conectividade
    
    Example:
        >>> geraGrafo(0, 5, 10, numC=10)  # 10 componentes para 5 vértices
        ComponentesInvalidasError: Número de vértices (5) insuficiente para 10 componentes
    """
    pass 