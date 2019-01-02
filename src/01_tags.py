#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Gera lista com todas as tags encontradas em uma lista de arquivos XML.
    
    Recebe: 
    - origem: diretorio de origem dos arquivos XML
    - destino: arquivo com lista de tags
"""

import sys
import xml.etree.ElementTree as xml
from os import listdir
from os.path import isfile, join
from collections import OrderedDict


__author__ = 'Roberto Nunes Mourao'
__version__ = '1.0.0'
__email__ =  'contato@mineration.com'


def exec_func(caminho, elem):
    "Constroi recursivamente o caminho de cada tag, desde a raiz."

    caminho += str(elem.tag) + ' '

    children = list(elem)
    if not children:
        elemList.append(caminho)
    else:
        for child in children:
            exec_func(caminho, child)


# recebe argumentos de chamada do modulo
argumentos = sys.argv[1:]
origem = argumentos[0]
destino = argumentos[1]

# recupera lista de arquivos XML
arquivos = [a for a in listdir(origem) if isfile(join(origem, a))]

# le cada arquivo XML, obtendo todas as tags mencionadas
elemList = []
for arquivo in arquivos:
    arvore = xml.parse(join(origem, arquivo))
    exec_func('', arvore.getroot())

# remove elementos repetidos e ordena
elemList = list(OrderedDict.fromkeys(elemList))
elemList.sort()

# salva arquivo de destino
with open(destino, 'w') as w:
    for e in elemList:
        w.write(e + '\n')
