#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Cria arquivos CSV a partir dos arquivos XML no formato de parser
    novo (Sovren). Os arquivos CSV tem como chave o nome do arquivo XML.

    Recebe: 
    - origem: diretorio de origem dos arquivos XML
    - destino: diretorio de destino dos arquivos CSV
"""

import xml.etree.ElementTree as xml
import sys
from os import listdir, makedirs
from os.path import isfile, join, exists, dirname
import pandas as pd
import string
import unicodedata
from datetime import datetime
from io import StringIO
import re


__author__ = 'Roberto Nunes Mourao'
__version__ = '1.0.0'
__email__ =  'contato@mineration.com'


def efetuar_parse(texto):
    "Limpa texto e tira todos os prefixos de tags, retornando raiz do XML."

    # retirar quebras de linha e textos inuteis
    texto = texto.replace(',', ' ') \
                 .replace('\n', ' ') \
                 .replace('\t', ' ') \
                 .lower()

    # retirar texto de prefixo de tags
    it = xml.iterparse(StringIO(texto))
    for _, el in it:
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1].replace('sov:', '')
    return it.root


def obtem_campos(elemento, chave=''):
    "Extrai recursivamente conteudo de um trecho de XML."

    # monta nome do campo
    if chave == '':
        chave = elemento.tag
    else:
        chave += '_' + elemento.tag

    # monta registros com informacoes, chave e valor
    filhos = list(elemento)
    if not filhos:
        if 'skillstaxonomyoutput' not in chave:
            if elemento.text:
                linha[chave] = elemento.text
            else:
                # campos sobre skills sao dados binarios, indicando
                # a existencia da skill
                if 'name' in elemento.attrib:
                    chave += '_' + elemento.attrib['name']
                    linha[chave] = 1

                # tempo de experiencia em determinada skill tambem
                # eh gravado
                if 'totalmonths' in elemento.attrib:
                    chave += '_totalmonths'
                    linha[chave] = elemento.attrib['totalmonths']
    else:
        for filho in filhos:
            obtem_campos(filho, chave)


# receber caminhos de entrada e de saida
caminho_xml = sys.argv[1]

# precisa receber o caminho dos XMLs
if not exists(dirname(caminho_xml)):
    raise RuntimeError('Diretório de XMLs inválido.')
caminho_csv = sys.argv[2]

# cria diretorio se esse nao existir
if not exists(dirname(caminho_csv)):
    makedirs(dirname(caminho_csv))

# trechos de interesse dos arquivos XML
trechos = {'structuredxmlresume':  ['contactinfo', 'schoolorinstitution', 'employerorg', 'language', 
                                    'licenseorcertification','qualifications', 'reference'], 
           'userarea' : ['culture', 'experiencesummary', 'personalinformation', 'traininghistory'] }

# cria tabelas
for tabela in trechos['structuredxmlresume'] + trechos['userarea']:
    exec(tabela + ' = []')

# le arquivos xml
arquivos = [a for a in listdir(caminho_xml) if isfile(join(caminho_xml, a)) and '.xml' in a]
for arquivo in arquivos:
    with open(join(caminho_xml, arquivo), 'r') as r:
        texto = r.read()
    
    # executa parse
    raiz = efetuar_parse(texto)

    for trecho in ['structuredxmlresume', 'userarea']:
        curriculo = raiz.find(trecho)

        # povoa tabelas
        tabelas = trechos[trecho]
        for tabela in tabelas:
            for item in curriculo.iterfind('.//' + tabela):
                linha =  { 'id' : arquivo }
                obtem_campos(item)
                exec(tabela + '.append(linha)')

# salva tabelas em arquivos CSV
for tabela in trechos['structuredxmlresume'] + trechos['userarea']:
    print(str(datetime.now()) + ' salvando ' + tabela)
    tab = None
    exec('tab = ' + tabela)
    pd.DataFrame(tab).to_csv(caminho_csv + tabela + '.csv', encoding='utf-8', index=False, sep=',')
