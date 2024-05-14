import pandas as pd
import os

# Função para calcular o custo com base no CNPJER
def custo_agenda(cnpj):
    if cnpj == '04391007000132':
        return 0.00964
    elif cnpj == '23399607000191':
        return 0.04185
    elif cnpj == '31345107000103':
        return 0.06   

def custo_interop(cnpj):
    if cnpj == '04391007000132':
        return 0.0
    elif cnpj == '23399607000191':
        return 0.00964
    elif cnpj == '31345107000103':
        return 0.00964   

def custo_total(cnpj):
    if cnpj == '04391007000132':
        return 0.00964
    elif cnpj == '23399607000191':
        return 0.05149
    elif cnpj == '31345107000103':
        return 0.06964   

arranjos_nuclea = {'003':'MCC','004':'VCC','006':'ACC', '007':'HCD','008':'ECC','010':'CBC','021':'HCC','025':'MCD','026':'VCD','027':'ECD','030':'CBD','043':'BCD'}


# Caminho para a pasta sincronizada do SharePoint
pasta = r'C:\Users\francesco.benedetto\MONEYPLUS\Produtos, Processos e Operações - Documentos\Recebíveis\Operacional\03 - Controle de agendas\Nuclea\Extrato\2024\04 - Abr'

# Lista para armazenar os DataFrames
dfs = []

# Percorre todos os arquivos na pasta
for arquivo in os.listdir(pasta):
    # Verifica se o arquivo é um arquivo CSV
    if arquivo.endswith('.csv'):
        # Cria o caminho completo para o arquivo
        caminho_arquivo = os.path.join(pasta, arquivo)
        print('Lendo arquivo:', caminho_arquivo)
        try:
            # Lê o arquivo CSV para um DataFrame, especificando o separador e tratando vírgulas como ponto flutuante
            df = pd.read_csv(caminho_arquivo, sep=';', dtype=str, thousands='.', decimal=',')
            # Adiciona o DataFrame à lista
            dfs.append(df)
        except Exception as e:
            print('Erro ao ler o arquivo:', caminho_arquivo)
            print('Erro:', e)

# Verifica se a lista de DataFrames está vazia
if not dfs:
    print('Nenhum DataFrame para concatenar')
else:
    # Concatena todos os DataFrames na lista
    df_final = pd.concat(dfs, ignore_index=True)

    # Escreve o DataFrame final para um arquivo CSV
    
colunas_selecionar = ['DtHrArq','CNPJER','CNPJCreddrSub','CodInstitdrArrajPgto','CNPJ_CPFUsuFinalRecbdr']

df_fatura = df_final[colunas_selecionar].copy().astype(str)

df_fatura['Agenda'] = df_fatura['DtHrArq'] + '-' + df_fatura['CNPJER'] + '-' + df_fatura['CNPJCreddrSub'] + '-' + df_fatura['CodInstitdrArrajPgto'] + '-' + df_fatura['CNPJ_CPFUsuFinalRecbdr']
df_fatura = df_fatura.drop_duplicates(subset=['Agenda'], keep='first')

df_fatura = df_fatura.drop(columns='Agenda')

# Aplicar a função à coluna 'CNPJER' para criar a nova coluna 'custo'
df_fatura['custo agenda'] = df_fatura['CNPJER'].apply(custo_agenda)
df_fatura['custo interop'] = df_fatura['CNPJER'].apply(custo_interop)
df_fatura['total'] = df_fatura['CNPJER'].apply(custo_total)
df_fatura['CodInstitdrArrajPgto'] = df_fatura['CodInstitdrArrajPgto'].replace(arranjos_nuclea)


df_fatura['custo agenda'] = df_fatura['custo agenda'].astype(float).apply(lambda x: f'{x:.5f}'.replace('.', ','))
df_fatura['custo interop'] = df_fatura['custo interop'].astype(float).apply(lambda x: f'{x:.5f}'.replace('.', ','))
df_fatura['total'] = df_fatura['total'].astype(float).apply(lambda x: f'{x:.5f}'.replace('.', ','))


# df_final.to_csv(r'C:/Users/francesco.benedetto/MONEYPLUS/Produtos, Processos e Operações - Documentos/Regulatório/Recebíveis/Operacional/03 - Controle de agendas/Nuclea/Extrato/Janfinal.csv', index=False)
# df_fatura.to_csv(r'C:\Users\francesco.benedetto\MONEYPLUS\Produtos, Processos e Operações - Documentos\Recebíveis\Operacional\03 - Controle de agendas\Nuclea\Extrato\2024\00 - Fatura Nuclea\04 - Abril_final.csv', sep=';', index=False)


# Saida de arquivos

diretorio = os.getcwd()
localSaida = os.path.join(diretorio, 'output2')
SaidaConsolidado = os.path.join(localSaida, 'consolidado.csv')
SaidaFinal = os.path.join(localSaida, 'MES - Final.csv')

df_final.to_csv(SaidaConsolidado, sep=';' ,index=False)
df_fatura.to_csv(SaidaFinal, sep=';', index=False)

print('Arquivo Nuclea')

