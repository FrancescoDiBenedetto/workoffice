import pandas as pd
from decimal import ROUND_HALF_UP, Decimal
import os

# Caminho dos arquivos
diretorio = os.getcwd()
CaminhoCRRC034 = os.path.join(diretorio, "input2", "Conciliacao_Nuclea", "CRRC034")
CaminhoCRRC039 = os.path.join(diretorio, "input2", "Conciliacao_Nuclea", "CRRC039")
CaminhoARRC018 = os.path.join(diretorio, "input2", "Agenda_Nuclea")

dic_arranjos_nuclea = {
    "003": "MCC",
    "004": "VCC",
    "006": "ACC",
    "007": "HCD",
    "008": "ECC",
    "010": "CBC",
    "021": "HCC",
    "025": "MCD",
    "026": "VCD",
    "027": "ECD",
    "030": "CBD",
    "043": "BCD",
}
lst_arranjos_gravames = ["003", "004", "006", "008", "021"]

"""
    - Leitura dos aruqivos 
Parte do código responsavel por ler a pasta e concatenar os arquivos em um único dataframe 
Pelos arquivos não terem um header damos os nomes das colunas conforme informado no manual de layouts
"""
# Tratando o arquivo CRRC034
lst_CRRC034 = []
lst_colunas_CRRC034 = [
    "tipo de registro",
    "ID operação",
    "Identificador Negociação Recebivel",
    "Tipo de negociação",
    "Vencimento operação",
    "Saldo devedor",
    "Valor da garantia",
    "Alcance Cred/Sub",
    "Periodicidade do recalculo",
    "Dia de recalculo",
    "Situação operação",
    "Credenciadora",
    "Registradora",
    "Titular",
    "Titular da conta",
    "ISPB",
    "Tipo de conta",
    "Agencia",
    "conta",
    "Conta pagamento",
    "Arranjo",
    "Usuário final recebedor",
]

# Percorre todos os arquivos na pasta
for arquivo in os.listdir(CaminhoCRRC034):
    # Verifica se o arquivo é um arquivo CSV
    if arquivo.endswith(".csv"):
        # Cria o caminho completo para o arquivo
        caminho_arquivo = os.path.join(CaminhoCRRC034, arquivo)
        print("Lendo arquivo:", caminho_arquivo)
        try:
            # Lê o arquivo CSV para um DataFrame, especificando o separador e tratando vírgulas como ponto flutuante
            df34 = pd.read_csv(
                caminho_arquivo,
                sep=";",
                header=None,
                names=lst_colunas_CRRC034,
                dtype=str,
                skiprows=1,
            )
            # print(df34)
            # Adiciona o DataFrame à lista
            lst_CRRC034.append(df34)
        except Exception as e:
            print("Erro ao ler o arquivo:", caminho_arquivo)
            print("Erro:", e)

# Verifica se a lista de DataFrames está vazia
if not lst_CRRC034:
    print("Nenhum DataFrame para concatenar")
else:
    # Concatena todos os DataFrames na lista
    df_final34 = pd.concat(lst_CRRC034, ignore_index=True)
    # print(df_final34)

# # gerar um excel com o CRRC034
# saida = os.path.join(diretorio,'output2', 'testeCRRC034.xlsx')
# df_final.to_excel(saida, index=False)


# Tratando o arquivo CRRC039
lst_CRRC039 = []
lst_colunas_CRRC039 = [
    "IndrTpReg",
    "CNPJ_CNPJBase_CPFUsuFinalRecebdr",
    "CNPJCreddrSub",
    "CNPJFincdr",
    "CodInstitdrArrajPgto",
    "DtOptin",
    "DtIniOptIn",
    "DtFimOptin",
    "IdentdCtrlOptIn",
    "IdentdCtrlOptOut",
    "IndrOptInForcaContrto",
    "IndrSit",
    "IdentdtrlReqSolicteOptIn",
    "IdentdtrlReqSolicteOptOut",
]

# Percorre todos os arquivos na pasta
for arquivo39 in os.listdir(CaminhoCRRC039):
    # Verifica se o arquivo é um arquivo CSV
    if arquivo39.endswith(".csv"):
        # Cria o caminho completo para o arquivo
        caminho_arquivo_39 = os.path.join(CaminhoCRRC039, arquivo39)
        print("Lendo arquivo:", caminho_arquivo_39)
        try:
            # Lê o arquivo CSV para um DataFrame, especificando o separador e tratando vírgulas como ponto flutuante
            df39 = pd.read_csv(
                caminho_arquivo_39,
                sep=";",
                header=None,
                names=lst_colunas_CRRC039,
                dtype=str,
                skiprows=1,
            )
            # print(list(df39))

            # Adiciona o DataFrame à lista
            lst_CRRC039.append(df39)
        except Exception as e:
            print("Erro ao ler o arquivo:", caminho_arquivo_39)
            print("Erro:", e)

# Verifica se a lista de DataFrames está vazia
if not lst_CRRC039:
    print("Nenhum DataFrame para concatenar")
else:
    # Concatena todos os DataFrames na lista
    df_final39 = pd.concat(lst_CRRC039, ignore_index=True)
    # print(df_final39)

# gerar um excel com o CRRC034
saida39 = os.path.join(diretorio, "output2", "testeCRRC039.xlsx")
df_final39.to_excel(saida39, index=False)

"""
    - Ligar os contratos com as agendas 
Usando o CRRC034 com base nas colunas 'CNPJ_CNPJBase_CPFUsuFinalRecebdr', 'CNPJCreddrSub', 'CodInstitdrArrajPgto'
temos a chave para filtrar o data frame do ARRC018

Vale lembrar que temos 2 tipos de contrato, alcance geral 'G' e especifico 'E'
Alcance geral não tem o campo 'Credenciadora' e deve seru usado outra regra
"""

# -> Lista de agendas presentes no CRRC034
# Lista para alcance geral
df_optin34_alcace_geral = df_final34.copy()
df_optin34_alcace_geral = df_optin34_alcace_geral[
    df_optin34_alcace_geral["Alcance Cred/Sub"] == "G"
]
st_cnpj_alcance_geral = set(df_optin34_alcace_geral["Usuário final recebedor"])
# print(st_cnpj_alcance_geral)

# Lista para alcance especifico
df_optin34_alcace_especifico = df_final34.copy()
st_cnpj_alcance_especifico = set(
    df_optin34_alcace_especifico["Usuário final recebedor"]
)
st_cnpj_alcance_especifico = st_cnpj_alcance_especifico - st_cnpj_alcance_geral
df_optin34_alcace_especifico = df_optin34_alcace_especifico[
    df_optin34_alcace_especifico["Alcance Cred/Sub"] == "E"
]
df_optin34_alcace_especifico = df_optin34_alcace_especifico[
    df_optin34_alcace_especifico["Usuário final recebedor"].isin(
        st_cnpj_alcance_especifico
    )
]
df_optin34_alcace_especifico["Agenda"] = (
    df_optin34_alcace_especifico["Usuário final recebedor"]
    + "-"
    + df_optin34_alcace_especifico["Credenciadora"]
    + "-"
    + df_optin34_alcace_especifico["Arranjo"]
)
conjunto_alcance_especifico = set(df_optin34_alcace_especifico["Agenda"])
# print(conjunto_alcance_especifico)
# print(st_cnpj_alcance_especifico)


# Lista de opt-in por força de contrato
df_optin39 = df_final39.copy()
st_conjunto_CNPJ_gravame = set(df_final34["Usuário final recebedor"])
df_optin39 = df_optin39[df_optin39["IndrOptInForcaContrto"] == "S"]
df_optin39 = df_optin39[
    df_optin39["CNPJ_CNPJBase_CPFUsuFinalRecebdr"].isin(st_conjunto_CNPJ_gravame)
]
df_optin39["Agenda"] = (
    df_optin39["CNPJ_CNPJBase_CPFUsuFinalRecebdr"]
    + "-"
    + df_optin39["CNPJCreddrSub"]
    + "-"
    + df_optin39["CodInstitdrArrajPgto"]
)
# print(df_optin39['Agenda'])


# Leitura da Agenda Nuclea - ARRC018
arquivo18 = os.listdir(CaminhoARRC018)
caminho_arquivo_18 = os.path.join(CaminhoARRC018, arquivo18[0])
print("Lendo arquivo:", caminho_arquivo_18)
df_agenda_Nuclea = pd.read_csv(
    caminho_arquivo_18, sep=";", dtype=str, thousands=".", decimal=","
)
df_agenda_Nuclea["Agenda"] = (
    df_agenda_Nuclea["CNPJ_CPFUsuFinalRecbdr"]
    + "-"
    + df_agenda_Nuclea["CNPJCreddrSub"]
    + "-"
    + df_agenda_Nuclea["CodInstitdrArrajPgto"]
)
# print(list(df_agenda_Nuclea))
# print(df_agenda_Nuclea['Agenda'])


"""
    -> Critérios para filtrar as agendas de contratos.
Se alcance geral - trazer toda a agenda
Se alcance específic - trazer as agendas gravamadas

"""

df_agenda_contrato_geral = df_agenda_Nuclea[
    df_agenda_Nuclea["CNPJ_CPFUsuFinalRecbdr"].isin(st_cnpj_alcance_geral)
]
df_agenda_contrato_especifico = df_agenda_Nuclea[
    df_agenda_Nuclea["Agenda"].isin(conjunto_alcance_especifico)
]
df_agenda_contrato = pd.concat(
    [df_agenda_contrato_geral, df_agenda_contrato_especifico]
)
# print(list(df_agenda_contrato))


# Montar uma agenda de resumo por CNPJ
df_agenda_resumo = df_agenda_contrato.copy()
lst_colunas_excluir = [
    "NomeJSON",
    "NomArq",
    "DtHrArq",
    "DtHrArqComplet",
    "CNPJER",
    "CNPJCreddrSub",
    "CodInstitdrArrajPgto",
    "DtPrevtLiquid",
    "VlrLivreAntecCreddrSub",
    "VlrPreContrd",
    "VlrOnusResTec",
    "CNPJ_CPFTitular",
    "UR-CORTE",
    "Agenda",
]

# Garantir precisão na soma usando a biblioteca decimal
for coluna in lst_colunas_excluir:
    df_agenda_resumo = df_agenda_resumo.drop(columns=coluna)

for column in ["VlrTotTitlar", "VlrComprtdOutrInst", "VlrComprtdInst", "VlrLivreTot"]:
    try:
        df_agenda_resumo[column] = df_agenda_resumo[column].apply(
            lambda x: Decimal(x.replace(",", "."))
        )
    except Exception as e:
        print(f"Erro ao converter valores na coluna {column}: {e}")

# Agrupar e somar os valores por chave 'UR'
df_agenda_resumo = df_agenda_resumo.groupby(
    "CNPJ_CPFUsuFinalRecbdr", as_index=False
).sum()
# print(df_agenda_resumo)


# Converter os valores para tipo float
for column in ["VlrTotTitlar", "VlrComprtdOutrInst", "VlrComprtdInst", "VlrLivreTot"]:
    try:
        df_agenda_resumo[column] = df_agenda_resumo[column].apply(lambda x: float(x))
    except Exception as e:
        print(f"Erro ao converter valores na coluna {column}: {e}")


# Ajustar o nome das colunas da agenda de resumo
lst_nome_colunas_resumo = [
    "CNPJ",
    "R$ Valor Constituido",
    "R$ Comprometido",
    "R$ Valor Onerado",
    "R$ Valor Livres",
]
assert len(lst_nome_colunas_resumo) == len(df_agenda_resumo.columns)
df_agenda_resumo.columns = lst_nome_colunas_resumo


# # gerar um csv com agenda de gravames
# saida18 = os.path.join(diretorio, "output2", "testeAgendaGravames.csv")
# df_agenda_contrato.to_csv(saida18,sep=';', index=False)

# # gerar um excel com agenda de resumo
# saida_resumo = os.path.join(diretorio, "output2", "testeAgendaGravamesResumo.xlsx")
# df_agenda_resumo.to_excel(saida_resumo, index=False)

print("Arquivo pronto!")
