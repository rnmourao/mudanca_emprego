#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Cria arquivos CSV a partir dos arquivos XML no formato de parser
    antigo. Os arquivos CSV tem como chave o nome do arquivo XML.
"""


import xml.etree.ElementTree as xml
from os import listdir
from os.path import isfile, join
import pandas as pd


__author__ = 'Roberto Nunes Mourao'
__version__ = '1.0.0'
__email__ =  'contato@mineration.com'

# caminhos de origem e de destino
CAMINHO = '../data/antigo/'
XMLS = CAMINHO + 'xml/'
CSVS = CAMINHO + 'csv/'

# prefixo encontrado em todas as tags do formato antigo
PREFIXO = '{http://home.textkernel.nl/2013-08-01}'


def limpa_informacao(tag, texto):
    "Executa limpeza de texto no titulo e no conteudo da tag."

    nome = tag
    nome = nome.replace(PREFIXO, '')
    valor = texto
    if valor is not None:
        valor = valor.strip()
        if valor == '':
            valor = None
    return nome, valor


def monta_tabela_um(raiz, arquivo, elemento):
    "Monta tabela de tags que sao unicas no arquivo XML."

    ramo = raiz.find(PREFIXO + elemento)
    dic = {'id' : arquivo}
    for r in ramo:
        nome, valor = limpa_informacao(r.tag, r.text)
        if nome is not None:
            dic[nome] = valor
    return dic


def monta_tabela_varios(raiz, arquivo, elemento):
    """
    Monta tabela de tags que podem aparecer mais de uma vez
    no arquivo XML.
    """

    lista = []
    for item in raiz.iter(PREFIXO + elemento):
        dic = {'id' : arquivo}
        for r in item:
            nome, valor = limpa_informacao(r.tag, r.text)
            if nome is not None:
               dic[nome] = valor
        lista.append(dic)
    return lista

# recupera lista de nomes de arquivos XML
arquivos = [a for a in listdir(XMLS) if isfile(join(XMLS, a)) and '.xml' in a]

# cria tabelas em branco
tab_pessoal = []
tab_outros = []
tab_educacao = []
tab_emprego = []
tab_computacao = []
tab_idioma = []
tab_soft = []

# cria tabelas com tags selecionadas previamente
for arquivo in arquivos:
    with open(join(XMLS, arquivo), 'r') as r:
        texto = r.read()
    
    texto = texto.replace('\n', ' ')

    raiz = xml.fromstring(texto)
    tab_pessoal.append(monta_tabela_um(raiz, arquivo, 'Personal'))
    tab_outros.append(monta_tabela_um(raiz, arquivo, 'CustomArea'))
    tab_educacao.extend(monta_tabela_varios(raiz, arquivo, 'EducationItem'))
    tab_emprego.extend(monta_tabela_varios(raiz, arquivo, 'EmploymentItem'))
    tab_computacao.extend(monta_tabela_varios(raiz, arquivo, 'ComputerSkill'))
    tab_idioma.extend(monta_tabela_varios(raiz, arquivo, 'LanguageSkill'))
    tab_soft.extend(monta_tabela_varios(raiz, arquivo, 'SoftSkill'))

# salva tabelas em arquivos CSV
tab_pessoal = pd.DataFrame(tab_pessoal).to_csv(CSVS + '02_pessoal.csv', encoding='utf-8', index=False, sep='|')
tab_outros = pd.DataFrame(tab_outros).to_csv(CSVS + '02_outros.csv', encoding='utf-8', index=False, sep='|')
tab_educacao = pd.DataFrame(tab_educacao).to_csv(CSVS + '02_educacao.csv', encoding='utf-8', index=False, sep='|')
tab_emprego = pd.DataFrame(tab_emprego).to_csv(CSVS + '02_emprego.csv', encoding='utf-8', index=False, sep='|')
tab_computacao = pd.DataFrame(tab_computacao).to_csv(CSVS + '02_computacao.csv', encoding='utf-8', index=False, sep='|')
tab_idioma = pd.DataFrame(tab_idioma).to_csv(CSVS + '02_idioma.csv', encoding='utf-8', index=False, sep='|')
tab_soft = pd.DataFrame(tab_soft).to_csv(CSVS + '02_soft.csv', encoding='utf-8', index=False, sep='|')
