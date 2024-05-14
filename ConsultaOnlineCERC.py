'''import pandas as pd 
import json
import os

# Diretório 
diretorio = os.getcwd()

# Input de arquivos 
pasta = os.path.join(diretorio, 'input2', 'Consulta_CERC')
NomeArquivo = os.listdir(pasta)


CaminhoJson = os.path.join(pasta)
# Ler o JSON para um DataFrame
with open(CaminhoJson) as f:
    data = json.load(f)

# Preencher arrays vazios em "pagamentos" e "titulares"
for agenda in data['agendas']:
    for unidade in agenda['unidadesRecebiveis']:
        if not unidade['pagamentos']:
            unidade['pagamentos'] = []
        if not unidade['titulares']:
            unidade['titulares'] = []

# Normalizar o JSON e criar DataFrame
dfMatriz = pd.json_normalize(data, 'agendas', ['protocoloRequisicao', 'documentoUsuarioFinalRecebedor'], record_prefix='agendas_')
'''

import pandas as pd
import json
import os

# Diretório 
diretorio = os.getcwd()

# Input de arquivos 
pasta = os.path.join(diretorio, 'input2', 'Consulta_CERC')
NomeArquivo = os.listdir(pasta)

# Lista para armazenar os dados JSON de todos os arquivos
dados_empilhados = []

# Iterar sobre cada arquivo JSON
for arquivo in NomeArquivo:
    caminho_json = os.path.join(pasta, arquivo)
    print('lendo arquivos: ', arquivo)
    # Ler o JSON e adicionar os dados à lista
    with open(caminho_json) as f:
        dados_arquivo = json.load(f)
        dados_empilhados.append(dados_arquivo)

# Empilhar todos os dados em um único objeto JSON
data = {}
for dados in dados_empilhados:
    for chave, valor in dados.items():
        if chave not in data:
            data[chave] = valor
        else:
            data[chave].extend(valor)

# Preencher arrays vazios em "pagamentos" e "titulares"
for agenda in data['agendas']:
    for unidade in agenda['unidadesRecebiveis']:
        if not unidade['pagamentos']:
            unidade['pagamentos'] = []
        if not unidade['titulares']:
            unidade['titulares'] = []

# Normalizar o JSON e criar DataFrame
dfMatriz = pd.json_normalize(data, 'agendas', ['protocoloRequisicao', 'documentoUsuarioFinalRecebedor'], record_prefix='agendas_')

# Adicionar as colunas 'protocoloRequisicao' e 'documentoUsuarioFinalRecebedor' após a normalização
dfMatriz['protocoloRequisicao'] = data['protocoloRequisicao']
dfMatriz['documentoUsuarioFinalRecebedor'] = data['documentoUsuarioFinalRecebedor']

# Explodir as informações de "unidadesRecebiveis" como novas linhas
dfMatriz = dfMatriz.explode('agendas_unidadesRecebiveis')

# Expandir as informações de "agendas_unidadesRecebiveis" em colunas
unidades_df = pd.json_normalize(dfMatriz['agendas_unidadesRecebiveis'])

# Concatenar o DataFrame original com as novas colunas
dfMatriz.reset_index(drop=True, inplace=True)
dfMatriz = pd.concat([dfMatriz, unidades_df], axis=1)

# Explodir as informações de "pagamentos" como novas linhas
dfPagamento = dfMatriz.explode('pagamentos')

# Expandir as informações de "pagamentos" em colunas
pagamentos_df = pd.json_normalize(dfPagamento['pagamentos'])

# Concatenar o DataFrame original com as novas colunas
dfPagamento.reset_index(drop=True, inplace=True)
dfPagamento = pd.concat([dfPagamento, pagamentos_df], axis=1)

# Manipulação do data frame paraformatação em excel
dfAgenda = dfMatriz.copy()
colunasExcluir1 = ['agendas_unidadesRecebiveis', 'protocoloRequisicao','constituicao', 'pagamentos', 'titulares','valorConstituidoAntecipacaoPre', 'valorBloqueado']
for i in colunasExcluir1:
    dfAgenda = dfAgenda.drop(columns=i)

dfDetalhe = dfPagamento.copy()
colunasExcluir2 = ['agendas_unidadesRecebiveis', 'protocoloRequisicao', 'constituicao', 'valorConstituidoTotal','valorConstituidoAntecipacaoPre', 'valorBloqueado', 'valorLivre', 'pagamentos', 'titulares','domicilioPagamento.nomeTitular', 'domicilioPagamento.compe']
for n in colunasExcluir2:
    dfDetalhe = dfDetalhe.drop(columns=n)

NomeColunas1 = ['Credenciadora', 'Arranjo', 'Registradora', 'Usuario final recebedor', 'Data de liquidação', 'Valor constituido', 'Valor total', 'Valor livre']
NomeColunas2 = ['Credenciadora', 'Arranjo', 'Registradora', 'Usuario final recebedor', 'Data de liquidação','Valor total', 'Regra DIV', 'Valor onerado', 'Valor a pagar', 'Beneficiario', 'Tipo info Pagamento', 'Prioridade', 'Valor constituido de efeito de contrato', 'Titular conta', 'Tipo conta', 'ISPB', 'Agencia', 'Conta']

assert len(NomeColunas1) == len(dfAgenda.columns)
assert len(NomeColunas2) == len(dfDetalhe.columns)

dfAgenda.columns = NomeColunas1
dfDetalhe.columns = NomeColunas2



# # Salvar o DataFrame em um arquivo Excel
arquivoSaida = os.path.join(diretorio, 'output2', 'ConsultaOline_CERC.xlsx')
with pd.ExcelWriter(arquivoSaida) as writer:
    dfAgenda.to_excel(writer,sheet_name='Extrato', index=False)
    dfDetalhe.to_excel(writer,sheet_name='Detalhe', index=False)
print('Arquivo pornto')
