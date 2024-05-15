from datetime import datetime
from workalendar.america import Brazil
import pandas as pd
import numpy as np
import os

# Caminho dos arquivos de consiliação
diretorio = os.getcwd()
CaminhoTARIFARIO = os.path.join(diretorio, "input2", "Conciliacao_Nuclea", "TARIFARIO", "tabelaprecos_nuclea.xlsx")
CaminhoCRRC034 = os.path.join(diretorio, "input2", "Conciliacao_Nuclea", "CRRC034")
CaminhoCRRC039 = os.path.join(diretorio, "input2", "Conciliacao_Nuclea", "CRRC039")
CaminhoCRRC042 = os.path.join(diretorio, "input2", "Conciliacao_Nuclea", "CRRC042")


"""
    - Leitura dos aruqivos 
Parte do código responsavel por ler a pasta e concatenar os arquivos em um único dataframe 
Pelos arquivos não terem um header damos os nomes das colunas conforme informado no manual de layouts
"""
# Montar um dicionario de preços
df_tarifario = pd.read_excel(CaminhoTARIFARIO, sheet_name='Planilha1')
df_registradora_pemanencia = pd.read_excel(CaminhoTARIFARIO, sheet_name='Planilha2', dtype=str)
dict_custo_evento = df_tarifario.set_index("Evento")["Tarifa"].to_dict()
dict_nome_evento = df_tarifario.set_index("Evento")["Nome"].to_dict()
dict_registradora_evento = df_registradora_pemanencia.set_index("CRED")["evento"].to_dict()

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
    "Usuário final recebedor"
].copy()


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

# Dicionarip de id e cnpj
dict_operacao_cnpj = df_final34.set_index("ID operação")[
    "Usuário final recebedor"
].to_dict()

# Conta para permanecia de URs
df_permanencia34 = df_final34[
    [
        "ID operação",
        "Vencimento operação",
        "Saldo devedor",
        "Alcance Cred/Sub",
        "Credenciadora",
        "Arranjo",
        "Usuário final recebedor",
    ]
].copy()
df_permanencia34 = df_permanencia34.dropna(subset='Usuário final recebedor')
df_permanencia34['Credenciadora'] = df_permanencia34['Credenciadora'].fillna(value='Alcance Geral')

# Calendario da data conciliada
cal = Brazil()
data_conciliacao = datetime.strptime(input("Data em yyyy-mm-dd: "), "%Y-%m-%d").date()
df_permanencia34['Vencimento operação'] =df_permanencia34['Vencimento operação'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").date())
df_permanencia34['URs pendentes'] = df_permanencia34.apply(lambda row: cal.get_working_days_delta(data_conciliacao, row['Vencimento operação']), axis=1)
df_permanencia34 = df_permanencia34.drop(columns=["Vencimento operação","Saldo devedor","Alcance Cred/Sub","Arranjo"])
df_permanencia34 = df_permanencia34.groupby(["ID operação", "Credenciadora", "Usuário final recebedor"], as_index=False).sum()
df_permanencia34['Evento'] = df_permanencia34['Credenciadora'].map(dict_registradora_evento)
df_permanencia34['Custo Evento'] = df_permanencia34['Evento'].map(dict_custo_evento)
df_permanencia34['Custo total'] = np.multiply(df_permanencia34['Custo Evento'], df_permanencia34['URs pendentes'])

# Soma das UR em estoque no mes subsequente
df_permanencia_mes = df_permanencia34[['URs pendentes', 'Evento']].copy()
df_permanencia_mes['data mes'] = data_conciliacao
df_permanencia_mes = df_permanencia_mes.groupby(['data mes','Evento'], as_index=False).sum()
df_permanencia_mes = df_permanencia_mes[['data mes','URs pendentes', 'Evento']]

# # gerar um excel com o CRRC034
# saida = os.path.join(diretorio,'output2', 'testeCRRC034.xlsx')
# df_final.to_excel(saida, index=False)

# # gerar um excel com o permanencia
# saida = os.path.join(diretorio,'output2', 'permanecia34.xlsx')
# df_permanencia34.to_excel(saida, index=False)

# # gerar um excel com o permanencia resumo
# saida = os.path.join(diretorio,'output2', 'permaneciaMes.xlsx')
# df_permanencia_mes.to_excel(saida, index=False)


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

# # gerar um excel com o CRRC034
# saida39 = os.path.join(diretorio, "output2", "testeCRRC039.xlsx")
# df_final39.to_excel(saida39, index=False)


# Tratando o arquivo CRRC039
lst_CRRC042 = []
lst_colunas_CRRC042 = [
    "Tipo de registro",
    "Data do arquivo",
    "Descrição do envio do arquivo",
    "Data e hora do arquivo",
    "Evento tarifavel",
    "Quantidade de URs constituidas",
    "Quantidade de URs não constituidas",
    "ID da operação",
    "Periodicidade do Recalculo",
]

# Percorre todos os arquivos na pasta
for arquivo42 in os.listdir(CaminhoCRRC042):
    # Verifica se o arquivo é um arquivo CSV
    if arquivo42.endswith(".csv"):
        # Cria o caminho completo para o arquivo
        caminho_arquivo_42 = os.path.join(CaminhoCRRC042, arquivo42)
        print("Lendo arquivo:", caminho_arquivo_42)
        try:
            # Lê o arquivo CSV para um DataFrame, especificando o separador e tratando vírgulas como ponto flutuante
            df42 = pd.read_csv(
                caminho_arquivo_42,
                sep=";",
                header=None,
                names=lst_colunas_CRRC042,
                dtype=str,
                skiprows=1,
            )
            # Adiciona o DataFrame à lista
            lst_CRRC042.append(df42)
        except Exception as e:
            print("Erro ao ler o arquivo:", caminho_arquivo_42)
            print("Erro:", e)

# Verifica se a lista de DataFrames está vazia
if not lst_CRRC042:
    print("Nenhum DataFrame para concatenar")
else:
    # Concatena todos os DataFrames na lista
    df_consolidado42 = pd.concat(lst_CRRC042, ignore_index=True)

# Soma de todas as URs por evento
df_consolidado42["URs Total"] = df_consolidado42[
    "Quantidade de URs constituidas"
].apply(lambda x: int(x)) + df_consolidado42[
    "Quantidade de URs não constituidas"
].apply(
    lambda x: int(x)
)
# print(df_consolidado42)

# # gerar um excel com o CRRC042
# saida42 = os.path.join(diretorio, "output2", "testeCRRC042.xlsx")
# df_consolidado42.to_excel(saida42, index=False)

df_recalculo = df_consolidado42[
    ["Data do arquivo", "ID da operação", "URs Total", "Evento tarifavel"]
].copy()
df_recalculo = df_recalculo[df_recalculo["Evento tarifavel"] == "000015"]
df_recalculo["EC"] = df_recalculo["ID da operação"].map(dict_operacao_cnpj)
df_recalculo = df_recalculo.drop_duplicates(subset="EC", keep="first")
df_recalculo = df_recalculo.drop(columns="EC")
df_recalculo = df_recalculo.drop(columns="ID da operação")
df_recalculo["URs Total"] = 1
# print(df_recalculo)

# dataframe de eventos consolidados por dia
df_eventos42 = df_consolidado42[
    ["Data do arquivo", "URs Total", "Evento tarifavel"]
].copy()
df_eventos42 = df_eventos42[df_eventos42["Evento tarifavel"] != "000015"]
df_eventos42 = pd.concat([df_eventos42, df_recalculo])
df_eventos42 = df_eventos42.groupby(
    ["Data do arquivo", "Evento tarifavel"], as_index=False
).sum()
df_eventos42 = df_eventos42[["Data do arquivo", "URs Total", "Evento tarifavel"]]
# print(df_eventos42)

# dataframe separado para os eventos de recálculo


# # gerar um excel com o CRRC042consolidado
# saida42consolidado = os.path.join(diretorio, "output2", "consolidadoCRRC042.xlsx")
# df_eventos42.to_excel(saida42consolidado, index=False)


"""
    -> Ler os arquivos ARRC018 e contabilizar quantas agendas foram recebidas.
"""

if True:
    # Função para calcular o custo com base no CNPJER
    def evento_agenda_nuclea(cnpj):
        if cnpj == "04391007000132":
            return 1
        else:
            return 1


    def evento_agenda_cerc(cnpj):
        if cnpj == "23399607000191":
            return 1
        else:
            return 0


    def evento_agenda_tag(cnpj):
        if cnpj == "31345107000103":
            return 1
        else:
            return 0


    def evento_agenda_b3(cnpj):
        if cnpj == "09346601000125":
            return 1
        else:
            return 0


    def custo_total(cnpj):
        if cnpj == "04391007000132":
            return 0.00964
        elif cnpj == "23399607000191":
            return 0.05149
        elif cnpj == "31345107000103":
            return 0.06964


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

    # Caminho para a pasta sincronizada do SharePoint
    pasta = r"C:\Users\francesco.benedetto\MONEYPLUS\Produtos, Processos e Operações - Documentos\Recebíveis\Operacional\03 - Controle de agendas\Nuclea\Extrato\2024\04 - Abr"

    # Lista para armazenar os DataFrames
    dfs = []

    # Percorre todos os arquivos na pasta
    for arquivo in os.listdir(pasta):
        # Verifica se o arquivo é um arquivo CSV
        if arquivo.endswith(".csv"):
            # Cria o caminho completo para o arquivo
            caminho_arquivo = os.path.join(pasta, arquivo)
            print("Lendo arquivo:", caminho_arquivo)
            try:
                # Lê o arquivo CSV para um DataFrame, especificando o separador e tratando vírgulas como ponto flutuante
                df = pd.read_csv(
                    caminho_arquivo, sep=";", dtype=str, thousands=".", decimal=","
                )
                # Adiciona o DataFrame à lista
                dfs.append(df)
            except Exception as e:
                print("Erro ao ler o arquivo:", caminho_arquivo)
                print("Erro:", e)

    # Verifica se a lista de DataFrames está vazia
    if not dfs:
        print("Nenhum DataFrame para concatenar")
    else:
        # Concatena todos os DataFrames na lista
        df_final = pd.concat(dfs, ignore_index=True)

        # Escreve o DataFrame final para um arquivo CSV

    lst_colunas_selecionar = [
        "DtHrArq",
        "CNPJER",
        "CNPJCreddrSub",
        "CodInstitdrArrajPgto",
        "CNPJ_CPFUsuFinalRecbdr",
    ]

    lst_colunas_remover = [
        "CNPJER",
        "CNPJCreddrSub",
        "CodInstitdrArrajPgto",
        "CNPJ_CPFUsuFinalRecbdr",
    ]


    df_consolidado_agenda = df_final[lst_colunas_selecionar].copy().astype(str)

    df_consolidado_agenda["Agenda"] = (
        df_consolidado_agenda["DtHrArq"]
        + "-"
        + df_consolidado_agenda["CNPJER"]
        + "-"
        + df_consolidado_agenda["CNPJCreddrSub"]
        + "-"
        + df_consolidado_agenda["CodInstitdrArrajPgto"]
        + "-"
        + df_consolidado_agenda["CNPJ_CPFUsuFinalRecbdr"]
    )
    df_consolidado_agenda = df_consolidado_agenda.drop_duplicates(
        subset=["Agenda"], keep="first"
    )

    df_consolidado_agenda = df_consolidado_agenda.drop(columns="Agenda")

    # Aplicar a função à coluna 'CNPJER' para criar a nova coluna 'origen da agenda'
    df_consolidado_agenda["Agenda Nuclea"] = df_consolidado_agenda["CNPJER"].apply(
        evento_agenda_nuclea
    )
    df_consolidado_agenda["Agenda CERC"] = df_consolidado_agenda["CNPJER"].apply(
        evento_agenda_cerc
    )
    df_consolidado_agenda["Agenda Tag"] = df_consolidado_agenda["CNPJER"].apply(
        evento_agenda_tag
    )
    df_consolidado_agenda["Agenda B3"] = df_consolidado_agenda["CNPJER"].apply(
        evento_agenda_b3
    )

    # Consolidar as infomações por data
    df_agenda_mes = df_consolidado_agenda.groupby("DtHrArq", as_index=False).sum()

    # Formatar o dataframe
    for column in lst_colunas_remover:
        df_agenda_mes = df_agenda_mes.drop(columns=column)

    df_agenda_mes["DtHrArq"] = pd.to_datetime(df_agenda_mes["DtHrArq"], format="%d/%m/%Y")
    df_agenda_mes["DtHrArq"] = df_agenda_mes["DtHrArq"].dt.strftime("%Y-%m-%d")

    # Separa e concatenar os eventos
    df_agenda_nuclea = df_agenda_mes[["DtHrArq", "Agenda Nuclea"]].copy()
    df_agenda_nuclea["Evento"] = "000005"

    df_agenda_cerc = df_agenda_mes[["DtHrArq", "Agenda CERC"]].copy()
    df_agenda_cerc["Evento"] = "C00005"

    df_agenda_tag = df_agenda_mes[["DtHrArq", "Agenda Tag"]].copy()
    df_agenda_tag["Evento"] = "T00005"

    df_agenda_b3 = df_agenda_mes[["DtHrArq", "Agenda B3"]].copy()
    df_agenda_b3["Evento"] = "B00005"

    lst_novas_colunas = ["Data do arquivo", "Quantidade", "Evento"]
    assert len(lst_novas_colunas) == len(df_agenda_nuclea.columns)
    assert len(lst_novas_colunas) == len(df_agenda_cerc.columns)
    assert len(lst_novas_colunas) == len(df_agenda_tag.columns)
    assert len(lst_novas_colunas) == len(df_agenda_b3.columns)
    assert len(lst_novas_colunas) == len(df_eventos42.columns)
    assert len(lst_novas_colunas) == len(df_permanencia_mes.columns)
    df_agenda_nuclea.columns = lst_novas_colunas
    df_agenda_cerc.columns = lst_novas_colunas
    df_agenda_tag.columns = lst_novas_colunas
    df_agenda_b3.columns = lst_novas_colunas
    df_eventos42.columns = lst_novas_colunas
    df_permanencia_mes.columns = lst_novas_colunas

    # concatenando todas os dataframes
    df_fatura = pd.concat(
        [df_agenda_nuclea, df_agenda_cerc, df_agenda_tag, df_agenda_b3, df_eventos42, df_permanencia_mes]
    )
    df_fatura["Nome Evento"] = df_fatura["Evento"].map(dict_nome_evento)
    df_fatura["Custo Evento"] = df_fatura["Evento"].map(dict_custo_evento)

    df_fatura["Custo Evento"] = df_fatura["Custo Evento"].apply(lambda x: float(x))
    print(type(df_fatura["Custo Evento"]))
    df_fatura["Quantidade"] = df_fatura["Quantidade"].apply(lambda x: float(x))
    print(type(df_fatura["Quantidade"]))
    df_fatura["Custo total"] = np.multiply(
        df_fatura["Custo Evento"], df_fatura["Quantidade"]
    )
    print(df_fatura)


    # # gerar um excel com o a fatura
    saidaFatura = os.path.join(diretorio, "output2", "Consolidado_Fatura_Nuclea.xlsx")
    with pd.ExcelWriter(saidaFatura) as writer:
        df_fatura.to_excel(writer,sheet_name='Fatura', index=False)
        df_final34.to_excel(writer,sheet_name='CRRC034',index=False)
        df_consolidado42.to_excel(writer,sheet_name='CRRC042', index=False)
        df_permanencia34.to_excel(writer,sheet_name='Permanencia', index=False)
