# -*- coding: utf-8 -*- #

import sys
import xml.etree.ElementTree as xml
from os import listdir
from os.path import isfile, join
from collections import OrderedDict


def exec_func(caminho, elem):
    caminho += str(elem.tag) + ' '

    children = list(elem)
    if not children:
        elemList.append(caminho)
    else:
        for child in children:
            exec_func(caminho, child)


argumentos = sys.argv[1:]

origem = argumentos[0]
destino = argumentos[1]

arquivos = [a for a in listdir(origem) if isfile(join(origem, a))]

elemList = []
for arquivo in arquivos:
    arvore = xml.parse(join(origem, arquivo))
    exec_func('', arvore.getroot())

elemList = list(OrderedDict.fromkeys(elemList))
elemList.sort()

with open(destino, 'w') as w:
    for e in elemList:
        w.write(e + '\n')