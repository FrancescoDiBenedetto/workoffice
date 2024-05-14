from decimal import ROUND_HALF_UP, Decimal
from datetime import datetime
import pandas as pd 
import json
import os

# Dicionario de arranjos 
arranjos_nuclea = {'003':'MCC','004':'VCC','006':'ACC', '007':'HCD','008':'ECC','010':'CBC','021':'HCC','025':'MCD','026':'VCD','027':'ECD','030':'CBD','043':'BCD'}

# Diretório 
diretorio = os.getcwd()


# Input de arquivos 
pasta = os.path.join(diretorio, 'input2', 'Consulta_Nuclea')
NomeArquivo = os.listdir(pasta)
CaminhoJson = os.path.join(pasta, NomeArquivo[0])


# Ler o arquivo json
with open(CaminhoJson) as f:
    data = json.load(f)


# Normalizar o JSON e criar DataFrame
dfMatriz = pd.json_normalize(data, 'titulares', ["cnpjCreddrSub", "codInstitdrArrajPgto", "cnpjOuCnpjBaseOuCpfUsuFinalRecbdr", "dtPrevtLiquid", 'vlrTot'])
dfMatriz = dfMatriz.astype(str)
dfMatriz['UR'] = dfMatriz['cnpjCreddrSub'] + '-' + dfMatriz['codInstitdrArrajPgto'] + '-' + dfMatriz['cnpjOuCnpjBaseOuCpfUsuFinalRecbdr'] + '-' + dfMatriz['dtPrevtLiquid'] + '-' + dfMatriz['vlrTot']
# print(list(dfMatriz))


# Soma das outras colunas
dfSoma = dfMatriz.copy()
colunasExcluir1 = ['cnpjOuCpfTitlar', 'vlrTotTitlar', 'domicilios','operacoesOutrasInstituicoes', 'cnpjCreddrSub', 'codInstitdrArrajPgto', 'cnpjOuCnpjBaseOuCpfUsuFinalRecbdr', 'dtPrevtLiquid', 'vlrTot']
for n in colunasExcluir1:
    dfSoma = dfSoma.drop(columns=n)
# print(dfSoma)

colunaValores = ['vlrComprtdOutrInst', 'vlrComprtdInst', 'vlrLivreTot', 'vlrLivreAntecCreddrSub', 'vlrPreContrd', 'vlrOnusResTec']

for column in colunaValores:
    try:
        dfSoma[column] = dfSoma[column].apply(lambda x: Decimal(x).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) if pd.notnull(x) and str(x).replace('.', '').replace('-', '').isdigit() else Decimal(0))
    except Exception as e:
        print(f"Erro ao converter valores na coluna {column}: {e}")

dfSoma = dfSoma.groupby('UR', as_index=False).sum()

vlrComprtdOutrInst = dfSoma.set_index('UR')['vlrComprtdOutrInst'].to_dict()
vlrComprtdInst = dfSoma.set_index('UR')['vlrComprtdInst'].to_dict()
vlrLivreTot = dfSoma.set_index('UR')['vlrLivreTot'].to_dict()
vlrLivreAntecCreddrSub = dfSoma.set_index('UR')['vlrLivreAntecCreddrSub'].to_dict()
vlrPreContrd = dfSoma.set_index('UR')['vlrPreContrd'].to_dict()
vlrOnusResTec = dfSoma.set_index('UR')['vlrOnusResTec'].to_dict()


# Fazer um novo data frame pra planilha de extrato
dfExtrato = dfMatriz.copy()
colunasExcluir2 = ['cnpjOuCpfTitlar', 'vlrTotTitlar', 'vlrComprtdOutrInst', 'vlrComprtdInst', 'vlrLivreTot', 'vlrLivreAntecCreddrSub', 'vlrPreContrd', 'vlrOnusResTec', 'domicilios', 'operacoesOutrasInstituicoes']
for i in colunasExcluir2:
    dfExtrato = dfExtrato.drop(columns=i)


# remover os duplicados  
dfExtrato = dfExtrato.drop_duplicates(subset=['UR'], keep='first')


# Trazer os valores de cada coluna
dfExtrato['vlrComprtdOutrInst'] = dfExtrato['UR'].map(vlrComprtdOutrInst)
dfExtrato['vlrComprtdInst'] = dfExtrato['UR'].map(vlrComprtdInst)
dfExtrato['vlrLivreTot'] = dfExtrato['UR'].map(vlrLivreTot)
dfExtrato['vlrLivreAntecCreddrSub'] = dfExtrato['UR'].map(vlrLivreAntecCreddrSub)
dfExtrato['vlrPreContrd'] = dfExtrato['UR'].map(vlrPreContrd)
dfExtrato['vlrOnusResTec'] = dfExtrato['UR'].map(vlrOnusResTec)
dfExtrato = dfExtrato.drop(columns='UR')


# Ajustar a formatação das colunas 
dfExtrato['codInstitdrArrajPgto'] = dfExtrato['codInstitdrArrajPgto'].replace(arranjos_nuclea)
colunaValores.append('vlrTot')
for col in colunaValores:
    dfExtrato[col] = dfExtrato[col].astype(float).apply(lambda x: f'{x:.2f}'.replace('.', ','))
dfExtrato['dtPrevtLiquid'] = dfExtrato['dtPrevtLiquid'].apply(lambda x: datetime.fromisoformat(x))
print(dfExtrato)

# # Salvar o DataFrame em um arquivo Excel
dfExtrato.to_csv(os.path.join(diretorio, 'output2', 'ConsultaOline_Nuclea.csv'),sep=';', index=False)
print('ok')
