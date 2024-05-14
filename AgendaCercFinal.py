import pandas
import os
import numpy
import openpyxl
import datetime
import time
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, NamedStyle
from decimal import Decimal, ROUND_HALF_UP
import re

# Marca o inico do processamento 
start_time = time.time()

# Diretório 
diretorio = os.getcwd()

# Input de arquivos 
BancoDados = os.path.join(diretorio, 'input2','Agenda_CERC', 'CERC.csv')
dfMatriz = pandas.read_csv(BancoDados, sep = ';')
dfMatriz = dfMatriz.astype('string')
print('Input - Concluido')

# Drop duplicates 
dfMatriz['UR'] = dfMatriz['Inst_Credenciadora_ou_Subcredenciadora']+'-' + dfMatriz['Usuario_Final_Recebedor']+'-' + dfMatriz['Arranjo_de_Pagamento']+ '-'+ dfMatriz['Data_de_Liquidacao']+ '-'+ dfMatriz['Valor_Constituido']
dfMatriz = dfMatriz.drop_duplicates(subset= ['UR'], keep= 'first')
print('Duplicatas - Removidas')

# Lista de UR
listaUR = dfMatriz.copy()

# Separar a coluna _listaUR por |
listaUR['_listaUR'] = listaUR['_listaUR'].str.split('|')

# Explodir a coluna _listaUR para ter uma linha para cada valor separado por |
listaUR = listaUR.explode('_listaUR')

# Verificar e tratar valores nulos ou não string em _listaUR
def split_list(x):
    if isinstance(x, str):
        return x.split(';')
    else:
        return []


# trazer as informações de valores dos dicionario
def efeito_de_contrato(UR):
    if UR in valor_receber:
        return valor_receber[UR]   
    else:
        return 0.00
    
def valor_onerado(UR):
    if UR in valor_solicitado:
        return valor_solicitado[UR]   
    else:
        return 0.00

# Aplicar a função split_list em _listaUR
listaUR['_listaUR'] = listaUR['_listaUR'].apply(split_list)

# Agora, separar cada valor em _listaUR por ;
# listaUR['_listaUR'] = listaUR['_listaUR'].apply(lambda x: x.split(';'))

# Criar novas colunas para cada valor separado por ;
separated_data = pandas.DataFrame(listaUR['_listaUR'].to_list(), columns=[f'Dado_{i+1}' for i in range(len(listaUR['_listaUR'].iloc[0]))])

# Redefinir o índice dos DataFrames
listaUR.reset_index(drop=True, inplace=True)
separated_data.reset_index(drop=True, inplace=True)

# Concatenar o DataFrame original com o DataFrame de dados separados
listaUR = pandas.concat([listaUR[['Inst_Credenciadora_ou_Subcredenciadora', 'Usuario_Final_Recebedor', 'Arranjo_de_Pagamento', 'Data_de_Liquidacao', 'Valor_Constituido', 'UR']], separated_data], axis=1)

# Planilha de descrição completa
print('Lista de URs prontas')

new_column_names = ['Inst_Credenciadora_ou_Subcredenciadora', 'Usuario_Final_Recebedor', 'Arranjo_de_Pagamento', 'Data_de_Liquidacao', 'Valor_Constituido', 'UR', 'CNPJ do titular do domicilio', 'Tipo de Conta', 'COMPE', 'ISPB', 'Agência', 'Número da Conta', 'Valor a pagar', 'Beneficiário', 'Dt Liquidação Efetiva', 'Valor da Liquidação Efetivo', 'Regra de divisão', 'Valor Onerado na UR', 'Tipo de Informação de Pagamento', 'Indicador de ordem de efeito', 'Valor Constituído do efeito de contrato na UR']
colunm_ajustar_int = ['Inst_Credenciadora_ou_Subcredenciadora', 'Usuario_Final_Recebedor', 'CNPJ do titular do domicilio', 'ISPB', 'Número da Conta', 'Beneficiário', 'Regra de divisão', 'Tipo de Informação de Pagamento', 'Indicador de ordem de efeito']
column_ajustar_float = ['Valor_Constituido','Valor a pagar', 'Valor Onerado na UR', 'Valor Constituído do efeito de contrato na UR']

assert len(new_column_names) == len(listaUR.columns)

listaUR.columns = new_column_names


# Ajustar as colunas para números tipo float e int
for coluna in column_ajustar_float:
    # Verificar se a célula não está vazia
    listaUR[coluna] = listaUR[coluna].apply(lambda x: float(x) if isinstance(x, str) and x.strip() else x)
    listaUR[coluna] = listaUR[coluna].apply(lambda x: x.replace('.', ',') if isinstance(x, str) else x)

print('for de float ok')

for coluna in colunm_ajustar_int:
    listaUR[coluna] = listaUR[coluna].apply(lambda x: ''.join(filter(str.isdigit, x)) if isinstance(x, str) and x.strip() else x)
    listaUR[coluna] = listaUR[coluna].apply(lambda x: int(x) if isinstance(x, str) and x.strip() else x)
    
print('for de int ok')

dfISPB = listaUR.copy()
dfTOTAL = listaUR.copy()


# Trocando ponto por virgula 
# dfMatriz
dfMatriz['Valor_Constituido'] = dfMatriz['Valor_Constituido'].astype(float).replace('.', ',')
dfMatriz['Valor_Constituido_antecipacao_pre_contratado'] = dfMatriz['Valor_Constituido_antecipacao_pre_contratado'].astype(float).replace('.', ',')
dfMatriz['Valor_Bloqueado'] = dfMatriz['Valor_Bloqueado'].astype(float).replace('.', ',')
dfMatriz['Valor_Livre'] = dfMatriz['Valor_Livre'].astype(float).replace('.', ',')
dfMatriz['Valor_Total_UR'] = dfMatriz['Valor_Total_UR'].astype(float).replace('.', ',')

print('Ponto por Virgula - Trocado')


# Tranformado CNPJ para numero inteiro 
# dfMatriz
dfMatriz['Entidade_Registradora'] = pandas.to_numeric(dfMatriz['Entidade_Registradora'], errors= 'coerce').astype('int64')
dfMatriz['Inst_Credenciadora_ou_Subcredenciadora'] = pandas.to_numeric(dfMatriz['Inst_Credenciadora_ou_Subcredenciadora'], errors= 'coerce').astype('int64')
dfMatriz['Usuario_Final_Recebedor'] = pandas.to_numeric(dfMatriz['Usuario_Final_Recebedor'], errors= 'coerce').astype('int64')
dfMatriz['Titular_da_Unidade_de_Recebivel'] = pandas.to_numeric(dfMatriz['Titular_da_Unidade_de_Recebivel'], errors= 'coerce').astype('int64')
dfMatriz['documentoFederal'] = pandas.to_numeric(dfMatriz['documentoFederal'], errors= 'coerce').astype('int64')


print('CNPJ tranformados para numeros inteiros')

# Foramtando a data
dfMatriz['Data_de_Liquidacao'] = pandas.to_datetime(dfMatriz['Data_de_Liquidacao']).dt.strftime('%d/%m/%Y')

print('data formatada')

# Dicionario de oneração sobre cada UR
colunas_remover_detalhe = ['Inst_Credenciadora_ou_Subcredenciadora', 'Usuario_Final_Recebedor', 'Arranjo_de_Pagamento', 'Data_de_Liquidacao', 'Valor_Constituido', 'CNPJ do titular do domicilio', 'Tipo de Conta', 'COMPE', 'ISPB', 'Agência', 'Número da Conta', 'Valor a pagar', 'Beneficiário', 'Dt Liquidação Efetiva', 'Valor da Liquidação Efetivo', 'Regra de divisão', 'Tipo de Informação de Pagamento', 'Indicador de ordem de efeito']

dfvalor_a_receber = listaUR.copy()
dfvalor_a_receber = dfvalor_a_receber[dfvalor_a_receber['ISPB'] == 11581339]

for R in colunas_remover_detalhe:
    dfvalor_a_receber = dfvalor_a_receber.drop(columns= R)

# Excluir linhas onde pelo menos uma das colunas contém um valor nulo
dfvalor_a_receber = dfvalor_a_receber.dropna(subset=['Valor Onerado na UR', 'Valor Constituído do efeito de contrato na UR'])


# Converter os valores para Decimal com precisão de duas casas decimais
for column in ['Valor Onerado na UR', 'Valor Constituído do efeito de contrato na UR']:
    try:
        dfvalor_a_receber[column] = dfvalor_a_receber[column].apply(lambda x: Decimal(x).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) if pandas.notnull(x) and str(x).replace('.', '').replace('-', '').isdigit() else Decimal(0))
    except Exception as e:
        print(f"Erro ao converter valores na coluna {column}: {e}")

# Agrupar e somar os valores por chave 'UR'
dfvalor_a_receber = dfvalor_a_receber.groupby('UR', as_index=False).sum()

# Verificar o DataFrame resultante
# print(dfvalor_a_receber)

valor_receber = dfvalor_a_receber.set_index('UR')['Valor Constituído do efeito de contrato na UR'].to_dict() 
valor_solicitado = dfvalor_a_receber.set_index('UR')['Valor Onerado na UR'].to_dict()

# print(valor_receber)

# Planilha de Valor a receber
dfISPB = dfISPB[dfISPB['ISPB'] == 11581339]


# Planilha resumo 
dfResumo = dfMatriz.copy()
dfResumo = dfResumo.drop(columns= ['Referencia_Externa'])
dfResumo = dfResumo.drop(columns= ['Entidade_Registradora'])
dfResumo = dfResumo.drop(columns= ['Titular_da_Unidade_de_Recebivel'])
dfResumo = dfResumo.drop(columns= ['Constituicao_da_Unidade_de_Recebivel'])
dfResumo = dfResumo.drop(columns= ['Valor_Bloqueado'])
dfResumo = dfResumo.drop(columns= ['Valor_Constituido_antecipacao_pre_contratado'])
dfResumo = dfResumo.drop(columns= ['Carteira'])
dfResumo = dfResumo.drop(columns= ['Valor_Total_UR'])
dfResumo = dfResumo.drop(columns= ['Data_hora_ultima_atualizacao_da_UR'])
dfResumo = dfResumo.drop(columns= ['_listaUR'])
dfResumo = dfResumo.drop(columns= ['codigoEmpresaTravaBancaria'])
dfResumo = dfResumo.drop(columns= ['empresaTravaBancaria'])
dfResumo = dfResumo.drop(columns= ['documentoFederal'])
dfResumo = dfResumo.drop(columns= ['bucket'])
dfResumo = dfResumo.drop(columns= ['pasta'])
print('Tabela de resumo - Feito')


#   trazer os valores soloicitados e constituidos por efeito de contrato

dfResumo['Valor_receber'] = (dfResumo['UR'].apply(efeito_de_contrato)).astype(float)
# dfResumo['Valor_solicitado'] = (dfResumo['UR'].apply(valor_onerado)).astype(float)
dfMatriz['Valor_receber'] = (dfMatriz['UR'].apply(efeito_de_contrato)).astype(float)
dfMatriz['Valor_solicitado'] = (dfMatriz['UR'].apply(efeito_de_contrato)).astype(float)


for A in ('codigoEmpresaTravaBancaria', 'empresaTravaBancaria', 'documentoFederal', 'bucket', 'pasta', 'UR'):
    dfMatriz = dfMatriz.drop(columns= [A])
# print(list(dfMatriz))

dfResumo = dfResumo.drop(columns= ['UR'])
dfResumo['Comprometido_outra_instituição'] = dfResumo['Valor_Constituido'] - dfResumo['Valor_Livre'] - dfResumo['Valor_receber']
dfResumo.loc[dfResumo['Comprometido_outra_instituição'] < 0, 'Comprometido_outra_instituição'] = 0
# print(dfResumo)

print('Somases de valores feito')

dfMatriz['_listaUR'] = dfMatriz['_listaUR'].astype(str)


# Salvando Planilhas 
if True:
    ArquivoSaida = os.path.join(diretorio, 'output2', f'Agenda_CERC_{pandas.Timestamp.now().date()}.xlsx')
    with pandas.ExcelWriter(ArquivoSaida, date_format= 'dd/mm/yyyy') as writer:
        dfMatriz.to_excel(writer, sheet_name= 'Completo', index = False)
        dfResumo.to_excel(writer, sheet_name= 'Resumo', index= False)
        dfISPB.to_excel(writer, sheet_name= 'Valor_a_receber', index= False)
        dfTOTAL.to_excel(writer, sheet_name= 'Domicilio bancario', index= False)

# Marcar o fim do processamento
end_time = time.time()
elapsed_time = (end_time - start_time)/60


# print(f"Tempo decorrido: {end_time} Segundos")
print(f"Tempo decorrido: {elapsed_time:.2f} minutos")

print('Arquivo Pronto \U0001F60A')