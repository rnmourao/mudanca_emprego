import pandas as pd
import numpy as np
import sys
from os import listdir
from os.path import isfile, join
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta as rd
import scipy.stats as stats
from copy import deepcopy


def extrai_tempo_empresa(linha, **kwargs):
    valor = None    
    
    if kwargs['inicio'] == True:
        nome = 'startdate'
    else:
        nome = 'enddate'
    
    if kwargs['tipo'] == 'ano':
        pos_ini = 0
        pos_fim = 4
    else:
        pos_ini = 5
        pos_fim = 7
        
    try:
        valor = linha['employerorg_positionhistory_' + nome + '_anydate'][pos_ini:pos_fim]
    except:
        pass
    
    try:
        valor = linha['employerorg_positionhistory_' + nome + '_yearmonth'][pos_ini:pos_fim]
    except:
        pass
    
    if kwargs['tipo'] == 'ano':
        try: 
            valor = int(linha['employerorg_positionhistory_' + nome + '_year'])
        except:
            pass
    
    try:
        valor = int(valor)
    except:
        valor = None
    
    return valor


# def extrai_tempo_escola(linha, **kwargs):
#     valor = None    
    
#     nome = kwargs['variavel']
        
#     if nome == 'degreedate':
#         comeco = 'schoolorinstitution_degree_'
#     else:
#         comeco = 'schoolorinstitution_degree_datesofattendance_'
    
#     if kwargs['tipo'] == 'ano':
#         pos_ini = 0
#         pos_fim = 4
#     else:
#         pos_ini = 5
#         pos_fim = 7
                
#     try:
#         valor = linha[comeco + nome + '_anydate'][pos_ini:pos_fim]
#     except:
#         pass

#     try:
#         valor = linha[comeco + nome + '_yearmonth'][pos_ini:pos_fim]
#     except:
#         pass

#     if kwargs['tipo'] == 'ano':
#         try: 
#             valor = int(linha[comeco + nome + '_year'])
#         except:
#             pass
    
#     try:
#         valor = int(valor)
#     except:
#         valor = None
    
#     return valor


def intervalo_datas(data_inicio, data_fim):
    r = rd(data_fim, data_inicio)
    quantidade = r.years * 12 + r.months + 1
    for n in range(quantidade):
        yield data_inicio + rd(months=n)


# recebe caminho onde se encontram os CSVs
caminho = sys.argv[1]

# dataframes
employerorg = None
schoolorinstitution = None
qualifications = None
language = None
culture = None
contactinfo = None
experiencesummary = None
personalinformation = None
reference = None

# Recuperando lista de ids completos
arquivos = [f for f in listdir(caminho) if isfile(join(caminho, f)) and '.csv' in f]

# Recuperando curriculos completos
for arquivo in arquivos:
    nome = arquivo.replace('.csv', '')
    exec(nome + ' = pd.read_csv(caminho + "' + arquivo + '", low_memory=False)')
dfs = [df for df in dir() if isinstance(eval(df), pd.DataFrame)]

# achatar startdate e enddate
employerorg['ano_inicio'] = employerorg.apply(extrai_tempo_empresa, axis=1, inicio=True, tipo='ano')
employerorg['mes_inicio'] = employerorg.apply(extrai_tempo_empresa, axis=1, inicio=True, tipo='mes')
employerorg['ano_fim'] = employerorg.apply(extrai_tempo_empresa, axis=1, inicio=False, tipo='ano')
employerorg['mes_fim'] = employerorg.apply(extrai_tempo_empresa, axis=1, inicio=False, tipo='mes')

# retirando registros com data de inicio e de fim invertidas
ls = []
for i, l in employerorg.iterrows():
    try:
        dt_ini = date(int(l['ano_inicio']), int(l['mes_inicio']), 1)
        dt_fim = date(int(l['ano_fim']), int(l['mes_fim']), 1)
    
        if dt_ini > dt_fim:
            ls.append(i)
    except:
        pass
    
employerorg.drop(ls, inplace=True)
employerorg.reset_index(drop=True, inplace=True)
employerorg.sort_values(by=['id', 'ano_fim', 'ano_inicio', 'mes_fim', 'mes_inicio'], ascending=False, inplace=True)

# tratar datas de fim
MES_INICIO_MODA = 1
MES_FIM_MODA = 12
ANO_FIM_CORRENTE = 2018
MES_FIM_CORRENTE = 9

guarda = None
for i, l in employerorg.iterrows():

    # guarda
    if guarda == l['id']:
        contador += 1
    else:
        guarda = l['id']
        contador = 1
        
    # montar datas do registro atual
    ano_inicio = l['ano_inicio']
    try:
        ano_inicio = int(ano_inicio)
    except:
        ano_inicio = None
    
    mes_inicio = l['mes_inicio']
    try:
        mes_inicio = int(mes_inicio)
    except:
        mes_inicio = None
        
    ano_fim = l['ano_fim']
    try:
        ano_fim = int(ano_fim)
    except:
        ano_fim = None
    
    mes_fim = l['mes_fim']
    try:
        mes_fim = int(mes_fim)
    except:
        mes_fim = None
    
   
    # empregos atuais
    if contador == 1:
        if ano_fim is None:
            ano_fim = ANO_FIM_CORRENTE
            
            if mes_fim is None:
                mes_fim = MES_FIM_CORRENTE
        else:
            if ano_fim == ANO_FIM_CORRENTE:
                if mes_fim is None:
                    mes_fim = MES_FIM_CORRENTE
            else:
                if mes_fim is None:
                    mes_fim = MES_FIM_MODA
                    
    # empregos anteriores
    else:
        if ano_fim is None:
            # ano_fim deve ser pelo menos igual ao ano_inicio
            if ano_inicio is not None:
                ano_fim = ano_inicio
            
            # agora, se o ano de inicio do emprego posterior for maior que o ano de inicio,
            # deve-se atualizar o ano_fim para o ano mais no futuro
            if guarda_ano_inicio > ano_inicio:
                ano_fim = guarda_ano_inicio
                
        if mes_fim is None:
            # mes_fim deve ser no minimo igual ao mes_inicio
            if ano_fim == ano_inicio:
                if mes_inicio is not None:
                    mes_fim = mes_inicio

            # agora, se o ano de inicio do emprego posterior for igual ao ano do emprego atual,
            # o mes_fim deve ser igual ao mes_inicio do emprego posterior
            # pode ocorrer, por azar, que o nao haja a informacao do mes de inicio do emprego
            # posterior, mas so o de fim. Por isso eh necessario verificar a data de fim do emprego
            # posterior.
            if ano_fim == guarda_ano_inicio:
                if guarda_mes_inicio is None:
                    if ano_fim == guarda_ano_fim:
                        if guarda_mes_fim is not None and guarda_mes_fim > mes_fim:
                            mes_fim = guarda_mes_fim
                    else:
                        mes_fim = MES_FIM_MODA
                else:
                    if guarda_mes_inicio > mes_fim:
                        mes_fim = guarda_mes_inicio

            # no caso do mes_fim atual ser menor que o do emprego posterior,
            # eh interessante colocar o mes_fim com dezembro
            else:
                if mes_fim is None or mes_fim < MES_FIM_MODA:
                    mes_fim = MES_FIM_MODA
    
    
    ## preencher mes de fim   
    employerorg.at[i, 'ano_fim'] = ano_fim
    employerorg.at[i, 'mes_fim'] = mes_fim
    
    
    # guarda emprego posterior
    guarda_ano_inicio = ano_inicio
    guarda_mes_inicio = mes_inicio
    guarda_ano_fim = ano_fim
    guarda_mes_fim = mes_fim

# Removendo mais alguns registros que não possuem informação de data.
ls = []
for i, l in employerorg.iterrows():
    if pd.isnull(l['ano_fim']) or pd.isnull(l['mes_fim']):
        ls.append(i)
    
employerorg.drop(ls, inplace=True)
employerorg.reset_index(drop=True, inplace=True)
employerorg.sort_values(by=['id', 'ano_fim', 'ano_inicio', 'mes_fim', 'mes_inicio'], ascending=True, inplace=True)

# Tratar datas de inicio
guarda = None
for i, l in employerorg.iterrows():

    # guarda
    if guarda == l['id']:
        contador += 1
    else:
        guarda = l['id']
        contador = 1
        
    # montar datas do registro atual
    ano_inicio = l['ano_inicio']
    try:
        ano_inicio = int(ano_inicio)
    except:
        ano_inicio = None
    
    mes_inicio = l['mes_inicio']
    try:
        mes_inicio = int(mes_inicio)
    except:
        mes_inicio = None
        
    ano_fim = l['ano_fim']
    try:
        ano_fim = int(ano_fim)
    except:
        ano_fim = None
    
    mes_fim = l['mes_fim']
    try:
        mes_fim = int(mes_fim)
    except:
        mes_fim = None
    
   
    # primeiro emprego
    if contador == 1:
        if ano_inicio is None:
            ano_inicio = ano_fim

        if mes_inicio is None:  
            mes_inicio = MES_INICIO_MODA

            if ano_inicio == ano_fim and mes_fim is not None and mes_fim < mes_inicio:
                mes_inicio = mes_fim
                    
    # empregos posteriores
    else:
        if ano_inicio is None:
            # ano_inicio deve ser no maximo igual ao ano_fim
            if ano_fim is not None:
                ano_inicio = ano_fim

            if guarda_ano_fim is not None and guarda_ano_fim < ano_inicio:
                ano_inicio = guarda_ano_fim
                
        if mes_inicio is None:
            # mes_inicio deve ser no maximo igual ao mes_fim
            if ano_inicio == ano_fim:
                if mes_fim is not None:
                    mes_inicio = mes_fim

            if ano_inicio == guarda_ano_fim:
                if guarda_mes_fim is None:
                    if ano_inicio == guarda_ano_inicio:
                        if guarda_mes_inicio is not None and guarda_mes_inicio > mes_inicio:
                            mes_inicio = guarda_mes_inicio
                    else:
                        mes_inicio = MES_INICIO_MODA
                else:
                    if guarda_mes_fim > mes_inicio:
                        mes_inicio = guarda_mes_fim

            else:
                if mes_inicio is None or mes_inicio > MES_INICIO_MODA:
                    mes_inicio = MES_INICIO_MODA
    
    
    ## preencher mes de inicio   
    employerorg.at[i, 'ano_inicio'] = ano_inicio
    employerorg.at[i, 'mes_inicio'] = mes_inicio
    
    
    # guarda emprego posterior
    guarda_ano_inicio = ano_inicio
    guarda_mes_inicio = mes_inicio
    guarda_ano_fim = ano_fim
    guarda_mes_fim = mes_fim

employerorg['data_inicio'] = employerorg.apply(lambda x: date(int(x['ano_inicio']), int(x['mes_inicio']), 1), axis=1)
employerorg['data_fim'] = employerorg.apply(lambda x: date(int(x['ano_fim']), int(x['mes_fim']), 1), axis=1)

# achatar startdate, enddate e degreedate
# schoolorinstitution['ano_inicio'] = schoolorinstitution.apply(extrai_tempo_escola, axis=1, variavel='startdate', tipo='ano')
# schoolorinstitution['mes_inicio'] = schoolorinstitution.apply(extrai_tempo_escola, axis=1, variavel='startdate', tipo='mes')
# schoolorinstitution['ano_fim'] = schoolorinstitution.apply(extrai_tempo_escola, axis=1, variavel='enddate', tipo='ano')
# schoolorinstitution['mes_fim'] = schoolorinstitution.apply(extrai_tempo_escola, axis=1, variavel='enddate', tipo='mes')
# schoolorinstitution['ano_graduacao'] = schoolorinstitution.apply(extrai_tempo_escola, axis=1, variavel='degreedate', tipo='ano')
# schoolorinstitution['mes_graduacao'] = schoolorinstitution.apply(extrai_tempo_escola, axis=1, variavel='degreedate', tipo='mes')

# MODA_MES_INICIO = 1
# MODA_MES_FIM = 12

# for i, l in schoolorinstitution.iterrows():
    
#     # montar datas do registro atual
#     ano_inicio = l['ano_inicio']
#     try:
#         ano_inicio = int(ano_inicio)
#     except:
#         ano_inicio = None
    
#     mes_inicio = l['mes_inicio']
#     try:
#         mes_inicio = int(mes_inicio)
#     except:
#         mes_inicio = None
        
#     ano_fim = l['ano_fim']
#     try:
#         ano_fim = int(ano_fim)
#     except:
#         ano_fim = None
    
#     mes_fim = l['mes_fim']
#     try:
#         mes_fim = int(mes_fim)
#     except:
#         mes_fim = None
    
#     ano_graduacao = l['ano_graduacao']
#     try:
#         ano_graduacao = int(ano_graduacao)
#     except:
#         ano_graduacao = None
    
#     mes_graduacao = l['mes_graduacao']
#     try:
#         mes_graduacao = int(mes_graduacao)
#     except:
#         mes_graduacao = None   
        
#     # preencher lacunas
#     if ano_inicio is None:
#         ano_inicio = ano_fim
    
#     if ano_fim is None:
#         ano_fim = ano_inicio
        
#     if ano_inicio is not None and mes_inicio is None:
#         mes_inicio = MODA_MES_INICIO
        
#     if ano_inicio is not None and mes_fim is None:
#         mes_fim = MODA_MES_FIM
        
#     if ano_graduacao is not None and mes_graduacao is None:
#         mes_graduacao = MODA_MES_FIM
        
#     ## preencher no dataframe   
#     schoolorinstitution.at[i, 'ano_inicio'] = ano_inicio
#     schoolorinstitution.at[i, 'mes_inicio'] = mes_inicio    
#     schoolorinstitution.at[i, 'ano_fim'] = ano_fim
#     schoolorinstitution.at[i, 'mes_fim'] = mes_fim    
#     schoolorinstitution.at[i, 'ano_graduacao'] = ano_graduacao
#     schoolorinstitution.at[i, 'mes_graduacao'] = mes_graduacao        

# ls = []
# for i, l in schoolorinstitution.iterrows():
#     if pd.isnull(l['ano_inicio']) and \
#        pd.isnull(l['mes_inicio']) and \
#        pd.isnull(l['ano_fim']) and \
#        pd.isnull(l['mes_fim']) and \
#        pd.isnull(l['ano_graduacao']) and \
#        pd.isnull(l['mes_graduacao']):
#         ls.append(i)
    
# schoolorinstitution.drop(ls, inplace=True)
# schoolorinstitution.reset_index(drop=True, inplace=True)
# schoolorinstitution['data_inicio'] = schoolorinstitution.apply(lambda x: date(int(x['ano_inicio']), int(x['mes_inicio']), 1), axis=1)
# schoolorinstitution['data_fim'] = schoolorinstitution.apply(lambda x: date(int(x['ano_fim']), int(x['mes_fim']), 1), axis=1)

# Criar dataframe no formato necessário para a modelagem
ls = []

# recuperar os ids unicos encontrados no employerorg
ls_ids = np.unique(employerorg['id']).tolist()

guarda = {'id': None}

# iterar sobre os ids
for i in ls_ids:
    
    temp = employerorg.loc[employerorg['id'] == i]
    
    # identificar data da primeira contratacao e data da ultima saida
    data_inicio = np.min(temp['data_inicio'])
    data_fim = np.max(temp['data_fim'])
    
    # lista para calcular tempo medio nos empregos
    ls_tempo_medio = []
    
    # iterar, mes a mes, criando um registro para cada id em cada mes
    for data in intervalo_datas(data_inicio, data_fim):
        if i == guarda['id']:
            linha = deepcopy(guarda)
        else:
            linha = {'id': i}
        
        
        # criar variavel alvo quando a data de fim for igual aa data iterada
        # incluir ou nao periodo desempregado na variavel alvo?
        if data in [x for x in temp['data_fim'].tolist() if x != date(2018, 7, 1)]:
            linha['label'] = 1
        else:
            linha['label'] = 0
            
            
        #### obter detalhes da experiencia profissional        
        
        # experiencia total em meses
        try:
            linha['experiencia_meses'] += 1
        except KeyError:
            linha['experiencia_meses'] = 1
        
        
        # tempo no emprego em meses
        if data in temp['data_inicio'].tolist():
            linha['tempo_emprego'] = 1
        else:
            linha['tempo_emprego'] += 1
        
        
        # media de tempo de mudanca de emprego
        if linha['label'] == 1:
            ls_tempo_medio.append(linha['tempo_emprego'])
            linha['tempo_medio'] = np.mean(ls_tempo_medio)
        else:
            linha['tempo_medio'] = np.mean(ls_tempo_medio + [linha['tempo_emprego']])
        
        
        # interacao entre tempo no emprego atual e tempo medio nos empregos
        linha['taxa_permanencia'] = linha['tempo_emprego'] / np.float(linha['tempo_medio'])
        
        
        # tempo na empresa (mudanca de cargos)
        try:
            empresa = temp.loc[(temp['data_inicio'] <= data) & (temp['data_fim'] >= data), 
                               'employerorg_employerorgname'].values[0]
        except IndexError:
            empresa = None
            
        try:
            if linha['empresa'] == empresa:
                linha['tempo_empresa'] += 1
            else:
                linha['tempo_empresa'] = 1
        except KeyError:
            linha['tempo_empresa'] = 1
        
        linha['empresa'] = empresa
        
        
        # skills
        COMECO_CAMPO = 'employerorg_positionhistory_userarea_positionhistoryuserarea_skill_'
        skills = [x for x in temp.columns if COMECO_CAMPO in x]
        datas_menores = temp.loc[temp['data_fim'] <= data]
        for skill in skills:
            if datas_menores[skill].sum() > 0:
                s = skill.replace(COMECO_CAMPO, '').replace('#', 'sharp').replace('.', 'dot').replace('+', 'p')
                try:
                    linha['skill_' + s] += 1
                except KeyError:
                    linha['skill_' + s] = 1
        
        
        #
        
        CAMPO_CARGO = 'employerorg_positionhistory_userarea_positionhistoryuserarea_normalizedtitle'
        
        try:
            cargo = temp.loc[(temp['data_inicio'] <= data) & (temp['data_fim'] >= data), CAMPO_CARGO].values[0]
        except IndexError:
            cargo = None
            
        if pd.notnull(cargo):
            if 'gestor' in cargo or 'gerente' in cargo or 'coordenador' in cargo:
                try:
                    linha['cargo_gerente'] += 1
                except KeyError:
                    linha['cargo_gerente'] = 1
            else:
                linha['cargo_gerente'] = 0

            if 'analista' in cargo or 'programador' in cargo or 'desenvolvedor' in cargo:
                try:
                    linha['cargo_analista'] += 1
                except KeyError:
                    linha['cargo_analista'] = 1
            else:
                linha['cargo_analista'] = 0

            if 'consultor' in cargo:
                try:
                    linha['cargo_consultor'] += 1
                except KeyError:
                    linha['cargo_consultor'] = 1
            else:
                linha['cargo_consultor'] = 0

            if 'estagi' in cargo:
                try:
                    linha['cargo_estagiario'] += 1
                except KeyError:
                    linha['cargo_estagiario'] = 1
            else:
                linha['cargo_estagiario'] = 0

            if 'engenheir' in cargo:
                try:
                    linha['cargo_engenheiro'] += 1
                except KeyError:
                    linha['cargo_engenheiro'] = 1
            else:
                linha['cargo_engenheiro'] = 0

        #
        
        # CAMPO_AUTONOMO = 'employerorg_positionhistory_userarea_positionhistoryuserarea_isselfemployed'

        # if 'trabalho_autonomo' not in linha:
        #     try:
        #         autonomo = temp.loc[(temp['data_inicio'] <= data) & (temp['data_fim'] >= data), 
        #                                 CAMPO_AUTONOMO].values[0]
        #     except IndexError:
        #         autonomo = None

        #     if pd.notnull(autonomo):
        #         linha['trabalho_autonomo'] = 1
        #     else:
        #         linha['trabalho_autonomo'] = 0

                
        # tempo no mesmo cargo        
        try:
            if linha['cargo'] == cargo:
                linha['tempo_cargo'] += 1
            else:
                linha['tempo_cargo'] = 1
        except KeyError:
            linha['tempo_cargo'] = 1
            
        linha['cargo'] = cargo
        
        
        # mudanca de localidade 
        CAMPO_MUNICIPIO = 'employerorg_positionhistory_orginfo_positionlocation_municipality'
        
        try:
            municipio = temp.loc[(temp['data_inicio'] <= data) & (temp['data_fim'] >= data), 
                                 CAMPO_MUNICIPIO].values[0]
        except IndexError:
            municipio = None  
            
        try:
            if linha['municipio_empresa'] == municipio:
                linha['tempo_municipio'] +=1
            else:
                linha['tempo_municipio'] = 1
        except KeyError:
            linha['tempo_municipio'] = 1
        
        linha['municipio_empresa'] = municipio
        
        
        #### acrescentar campos a partir das outras tabelas
        
        # faculdade
        # CURSO_CAMPO = 'schoolorinstitution_degree_degreemajor_name'
        # NIVEL_CAMPO = 'schoolorinstitution_degree_userarea_degreeuserarea_normalizeddegreetype'

        # datas_menores = schoolorinstitution.loc[(schoolorinstitution['id'] == i) & 
        #                                         (schoolorinstitution['data_fim'] <= data)]

        # for j, cursos in datas_menores.iterrows():
        #     if cursos[NIVEL_CAMPO] in ['bachelors', 'bsc', 'doctorate', 'masters', 
        #                                          'mba', 'msc', 'some college']: 
                
        #         if pd.notnull(cursos[CURSO_CAMPO]):
        #             if 'administracao' in cursos[CURSO_CAMPO] or 'gest' in cursos[CURSO_CAMPO] or \
        #                'geren' in cursos[CURSO_CAMPO]:
        #                 try:
        #                     linha['curso_administracao'] += 1
        #                 except KeyError:
        #                     linha['curso_administracao'] = 1

        #             if 'comput' in cursos[CURSO_CAMPO] or 'desenv' in cursos[CURSO_CAMPO] or \
        #                'inform' in cursos[CURSO_CAMPO]:
        #                 try:
        #                     linha['curso_computacao'] += 1
        #                 except KeyError:
        #                     linha['curso_computacao'] = 1

        #             if 'engenh' in cursos[CURSO_CAMPO]:
        #                 try:
        #                     linha['curso_engenharia'] += 1
        #                 except KeyError:
        #                     linha['curso_engenharia'] = 1
        
        ##
 
        # try:
        #     localizacao = contactinfo.loc[contactinfo['id'] == i, 
        #                                   'contactinfo_contactmethod_postaladdress_region'].values[0]
        # except IndexError:
        #     localizacao = None
        
        # locs = [x for x in linha.keys() if 'loc-' in x]
        # for lc in locs:
        #     linha[lc] = 0
        
        # if pd.notnull(localizacao):
        #     linha['loc-' + localizacao] = 1
        # else:
        #     linha['loc-br-df'] = 1
        
        ##
        # try:
        #     pais_origem = culture.loc[culture['id'] == i,
        #                               'culture_country'].values[0]
        # except IndexError:
        #     pais_origem = None
            
        # if pd.notnull(pais_origem):
        #     linha['pais-origem-' + pais_origem] = 1
        # else:
        #     linha['pais-origem-br'] = 1
                    
        #
        # try:
        #     idioma_nativo = culture.loc[culture['id'] == i,
        #                                 'culture_language'].values[0]
        # except IndexError:
        #     idioma_nativo = None
            
        # if pd.notnull(idioma_nativo):
        #     linha['idioma-nativo-' + idioma_nativo] = 1
        # else:
        #     linha['idioma-nativo-pt'] = 1
        
        ##
        
        if 'idioma-total' not in linha:
            idiomas = language.loc[language['id'] == i]
            linha['idioma-total'] = len(idiomas)

            for index, idioma in idiomas.iterrows():
                nome_idioma = idioma['language_languagecode']

                if idioma['language_read'] == True:
                    linha['idioma-' + nome_idioma + '-le'] = 1
                if idioma['language_speak'] == True:
                    linha['idioma-' + nome_idioma + '-fala'] = 1
                if idioma['language_write'] == True:
                    linha['idioma-' + nome_idioma + '-escreve'] = 1

        #
        if 'homem' not in linha and 'mulher' not in linha:
            try:
                sexo = personalinformation.loc[personalinformation['id'] == i,
                                               'personalinformation_gender'].values[0]
            except IndexError:
                sexo = None
                
            if pd.notnull(sexo):
                if sexo == 'male':
                    linha['homem'] = 1

                if sexo == 'female':
                    linha['mulher'] = 1                
            else:
                linha['homem'] = 0
                linha['mulher'] = 0
            
        #
        
        if 'solteiro' not in linha and 'casado' not in linha:
            try:
                estado_civil = personalinformation.loc[personalinformation['id'] == i,
                                                       'personalinformation_maritalstatus'].values[0]
            except IndexError:
                estado_civil = None
            
            if pd.isnull(estado_civil):
                estado_civil = ''
                
            if estado_civil == 'single' or estado_civil == 'separated' or estado_civil == 'divorced':
                linha['solteiro'] = 1
            else:
                linha['solteiro'] = 0

            if estado_civil == 'married':
                linha['casado'] = 1
            else:
                linha['casado'] = 0                    
        #
        
        # if 'idade' not in linha:
        #     try:
        #         data_nascimento = personalinformation.loc[personalinformation['id'] == i,
        #                                                   'personalinformation_dateofbirth'].values[0]
        #     except IndexError:
        #         data_nascimento = None
                
        #     if pd.notnull(data_nascimento):
        #         dt_nsc = date(int(data_nascimento[0:4]), 
        #                       int(data_nascimento[5:7]), 
        #                       int(data_nascimento[8:10]))
        #         r = rd(data, dt_nsc)
        #         idade = r.years * 12 + r.months + 1
        #         linha['idade'] = idade
        #     else:
        #         linha['idade'] = 0
        # else:
        #     if linha['idade'] > 0:
        #         linha['idade'] += 1
        
        #
        
        if 'tem_cnh' not in linha:
            try:
                tem_cnh = personalinformation.loc[personalinformation['id'] == i,
                                              'personalinformation_drivinglicense'].values[0]
            except IndexError:
                tem_cnh = None
                
            if pd.notnull(tem_cnh):
                linha['tem_cnh'] = 1
            else:
                linha['tem_cnh'] = 0
        
        # 
        
        # if 'sal_pretendido' not in linha:
        #     try:
        #         salario_pretendido = personalinformation.loc[personalinformation['id'] == i, 
        #                                                      'personalinformation_requiredsalary'].values[0]
        #     except IndexError:
        #         salario_pretendido = None

        #     if pd.notnull(salario_pretendido):
        #         linha['sal_pretendido'] = salario_pretendido
        #     else:
        #         linha['sal_pretendido'] = 0
        
        #
        
        # if 'tem_familia' not in linha:
        #     try:
        #         tem_familia = personalinformation.loc[personalinformation['id'] == i, 
        #                                               'personalinformation_familycomposition'].values[0]
        #     except IndexError:
        #         tem_familia = None

        #     if pd.notnull(tem_familia):
        #         linha['tem_familia'] = 1
        #     else:
        #         linha['tem_familia'] = 0

        #
        
        # if 'tem_lugar_nasc' in linha:
        #     try:
        #         lugar_nasc = personalinformation.loc[personalinformation['id'] == i,
        #                                             'personalinformation_birthplace'].values[0]
        #     except IndexError:
        #         lugar_nasc = None

        #     if pd.notnull(lugar_nasc):
        #         linha['tem_lugar_nasc'] = 1
        #     else:
        #         linha['tem_lugar_nasc'] = 0
        
        #
        
        # if 'tem_observacoes' in linha:
        #     try:
        #         tem_observacoes = experiencesummary.loc[experiencesummary['id'] == id, 
        #                                                 'experiencesummary_attentionneeded'].values[0]
        #     except IndexError:
        #         tem_observacoes = None

        #     if pd.notnull(tem_observacoes):
        #         linha['tem_observacoes'] = 1
        #     else:
        #         linha['tem_observacoes'] = 0
        
        #
        
        # if 'tem_website' in linha:
        #     try:
        #         tem_website = contactinfo.loc[contactinfo['id'] == i,
        #                                      'contactinfo_contactmethod_internetwebaddress'].values[0]
        #     except IndexError:
        #         tem_website = None

        #     if pd.notnull(tem_website):
        #         linha['tem_website'] = 1
        #     else:
        #         linha['tem_website'] = 0
        
        #
        
        # if 'tem_qualificacoes' in linha:
        #     try:
        #         tem_qualificacoes = qualifications.loc[qualifications['id'] == i, 'id'].values[0]
        #     except IndexError:
        #         tem_qualificacoes = None
                
        #     if pd.notnull(tem_qualificacoes):
        #         linha['tem_qualificacoes'] = 1
        #     else:
        #         linha['tem_qualificacoes'] = 0
        
        #
        
        # if 'tem_referencias' in linha:
        #     try:
        #         tem_referencias = reference.loc[reference['id'] == i, 'id'].values[0]
        #     except IndexError:
        #         tem_referencias = None

        #     if pd.notnull(tem_referencias):
        #         linha['tem_referencias'] = 1
        #     else:
        #         linha['tem_referencias'] = 0                
        
        # manter guarda atualizada        
        guarda = deepcopy(linha)
        
        # criar linha
        ls.append(linha)

# criar dataframe 
df = pd.DataFrame(ls)
df = df.fillna(0)

# selecionar somente colunas importantes
df = df[['label', 'experiencia_meses', 'homem', 'idioma-en-fala', 'idioma-en-le', 'skill_estagio', 'solteiro', 'taxa_permanencia', 'tem_cnh', 'tempo_cargo', 'tempo_emprego', 'tempo_empresa', 'tempo_municipio']]

df.to_csv('../data/df.csv', index=False)