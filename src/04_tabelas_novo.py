# -*- coding: utf-8 -*- #
import xml.etree.ElementTree as xml
from os import listdir
from os.path import isfile, join
import pandas as pd
import string
import locale

locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

def efetuar_parse(texto):
    from StringIO import StringIO
    import xml.etree.ElementTree as ET

    it = ET.iterparse(StringIO(texto))
    for _, el in it:
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1]  # tirar todos prefixo em chaves {}
    return it.root


def obtem_campos(elemento, chave=''):
    chave += '_' + str(elemento.tag)
    filhos = list(elemento)
    if not filhos:
        linha[chave] = elemento.text
    else:
        for filho in filhos:
            obtem_campos(filho, chave)


caminho = '/home/mourao/mudanca_emprego/data/novo/'
caminho_xml = caminho + 'xml/'
caminho_csv = caminho + 'csv/'

tabelas = ['contactmethod', 'schoolorinstitution', 'employerorg', 'language', 'licenseorcertification','qualifications', 'reference', 'culture', 'experiencesummary', 'personalinformation', 'traininghistory']

# cria tabelas
for tabela in tabelas:
    exec(tabela + ' = []')

# ler arquivos xml
arquivos = [a for a in listdir(caminho_xml) if isfile(join(caminho_xml, a)) and '.xml' in a]
for arquivo in arquivos:
    with open(join(caminho_xml, arquivo), 'r') as r:
        texto = r.read()
    
    # retirar quebras de linha e textos inuteis
    texto = ''.join(x for x in texto if x in string.printable).replace(',', ' ').lower()

    # executar parse
    raiz = efetuar_parse(texto)

    curriculo = raiz.find('structuredxmlresume')

    # povoar tabelas
    for tabela in tabelas:
        for item in curriculo.iterfind('.//' + tabela):
            linha =  { 'id' : arquivo }
            obtem_campos(item)
            exec(tabela + '.append(linha)')

for tabela in tabelas:
    tab = None
    exec('tab = ' + tabela)
    pd.DataFrame(tab).to_csv(caminho_csv + tabela + '.csv', encoding='utf-8', index=False, sep=',')

# IdValue
# RevisionDate
# ResumeQuality