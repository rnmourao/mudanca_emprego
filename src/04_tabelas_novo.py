# -*- coding: utf-8 -*- #
import xml.etree.ElementTree as xml
from os import listdir
from os.path import isfile, join
import pandas as pd
import string
import unicodedata
from datetime import datetime


def efetuar_parse(texto):
    'Tirar todos os prefixos de tags.'

    from StringIO import StringIO
    import xml.etree.ElementTree as ET

    it = ET.iterparse(StringIO(texto))
    for _, el in it:
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1].replace('sov:', '')
    return it.root


def obtem_campos(elemento, chave=''):
    'Extrair recursivamente conteudo de um trecho de XML.'

    if chave == '':
        chave = elemento.tag
    else:
        chave += '_' + elemento.tag
    filhos = list(elemento)
    if not filhos:
        if 'skillstaxonomyoutput' not in chave:
            if elemento.text:
                linha[chave] = elemento.text
            else:
                if 'name' in elemento.attrib:
                    chave += '_' + elemento.attrib['name']
                    linha[chave] = 1

                if 'totalmonths' in elemento.attrib:
                    chave += '_totalmonths'
                    linha[chave] = elemento.attrib['totalmonths']
    else:
        for filho in filhos:
            obtem_campos(filho, chave)


caminho = '/home/mourao/mudanca_emprego/data/novo/'
caminho_xml = caminho + 'xml/'
caminho_csv = caminho + 'csv/'

trechos = {'structuredxmlresume':  ['contactinfo', 'schoolorinstitution', 'employerorg', 'language', 
                                    'licenseorcertification','qualifications', 'reference'], 
           'userarea' : ['culture', 'experiencesummary', 'personalinformation', 'traininghistory'] }

# cria tabelas
for tabela in trechos['structuredxmlresume'] + trechos['userarea']:
    exec(tabela + ' = []')

# ler arquivos xml
arquivos = [a for a in listdir(caminho_xml) if isfile(join(caminho_xml, a)) and '.xml' in a]
i = 0
for arquivo in arquivos:
    i += 1
    print  int(100*i/float(len(arquivos))), arquivo
    with open(join(caminho_xml, arquivo), 'r') as r:
        texto = r.read()
    
    # retirar quebras de linha e textos inuteis
    texto = unicodedata.normalize('NFKD', unicode(texto, 'utf-8')) \
                        .encode('ascii', 'ignore') \
                        .replace(',', ' ') \
                        .replace('\n', ' ') \
                        .replace('\t', ' ') \
                        .lower()

    # executar parse
    raiz = efetuar_parse(texto)

    for trecho in ['structuredxmlresume', 'userarea']:
        curriculo = raiz.find(trecho)

        # povoar tabelas
        tabelas = trechos[trecho]
        for tabela in tabelas:
            for item in curriculo.iterfind('.//' + tabela):
                linha =  { 'id' : arquivo }
                obtem_campos(item)
                exec(tabela + '.append(linha)')

for tabela in trechos['structuredxmlresume'] + trechos['userarea']:
    print str(datetime.now()) + ' salvando ' + tabela
    tab = None
    exec('tab = ' + tabela)
    pd.DataFrame(tab).to_csv(caminho_csv + tabela + '.csv', encoding='utf-8', index=False, sep=',')

# RevisionDate
# ResumeQuality
