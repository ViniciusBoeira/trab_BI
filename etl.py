import pandas as pd
import glob
from sqlalchemy import create_engine, text

engine = create_engine("postgresql+psycopg2://postgres:root@localhost:5432/BI")

#Extração 
caminho = "dados/Fatura_*.csv"
arquivos = glob.glob(caminho)
lista_df = []

for arquivo in arquivos:
    df = pd.read_csv(arquivo, sep=";", encoding="utf-8")
    lista_df.append(df)

dados = pd.concat(lista_df, ignore_index=True)

#Transformação 

#Converter data
dados["Data de Compra"] = pd.to_datetime(dados["Data de Compra"], format="%d/%m/%Y")

#Tratar valores vazios na Categoria
dados["Categoria"] = dados["Categoria"].replace("-", "Nao categorizado")

#Converter valores numéricos
cols_numericas = ["Valor (em R$)", "Valor (em US$)", "Cotação (em R$)"]
for col in cols_numericas:
    dados[col] = pd.to_numeric(dados[col], errors="coerce").fillna(0)

#Tratar parcelas
def tratar_parcelas(valor):
    if "/" in str(valor):
        try:
            p, t = str(valor).split("/")
            return int(p), int(t)
        except:
            return 1, 1
    return 1, 1

dados['num_parcela'], dados['total_parcelas'] = zip(*dados['Parcela'].map(tratar_parcelas))

#Carga
#Carregar Staging
dados.to_sql("staging_transacoes", engine, if_exists="replace", index=False)

# Orquestração do SQL Dimensional
with engine.begin() as conn:
    print("iniciando dimensões...")
    
    #Limpar tabelas (Ordem correta por causa das FKs)
    conn.execute(text("TRUNCATE TABLE fato_transacao CASCADE;"))
    conn.execute(text("TRUNCATE TABLE dim_categoria, dim_estabelecimento, dim_titular, dim_data CASCADE;"))

    #Inserir Dimensões
    conn.execute(text("""
        INSERT INTO dim_categoria (id_categoria, nome_categoria)
        SELECT ROW_NUMBER() OVER (), "Categoria" FROM (SELECT DISTINCT "Categoria" FROM staging_transacoes) as sub;
    """))

    conn.execute(text("""
        INSERT INTO dim_estabelecimento (id_estabelecimento, nome_estabelecimento)
        SELECT ROW_NUMBER() OVER (), "Descrição" FROM (SELECT DISTINCT "Descrição" FROM staging_transacoes) as sub;
    """))

    conn.execute(text("""
        INSERT INTO dim_titular (id_titular, nome_titular)
        SELECT ROW_NUMBER() OVER (), "Nome no Cartão" FROM (SELECT DISTINCT "Nome no Cartão" FROM staging_transacoes) as sub;
    """))

    conn.execute(text("""
        INSERT INTO dim_data (id_data, data, dia, mes, ano, trimestre, dia_semana)
        SELECT 
            ROW_NUMBER() OVER (),
            dt,
            EXTRACT(DAY FROM dt),
            EXTRACT(MONTH FROM dt),
            EXTRACT(YEAR FROM dt),
            EXTRACT(QUARTER FROM dt),
            EXTRACT(DOW FROM dt)
        FROM (SELECT DISTINCT "Data de Compra" as dt FROM staging_transacoes) as sub;
    """))

    print("Carregando Tabela Fato...")
    #Inserir Fato relacionando IDs
    conn.execute(text("""
        INSERT INTO fato_transacao (
            id_data, id_titular, id_categoria, id_estabelecimento, 
            valor_brl, valor_usd, cotacao, num_parcela, total_parcelas
        )
        SELECT 
            d.id_data, t.id_titular, c.id_categoria, e.id_estabelecimento,
            s."Valor (em R$)", s."Valor (em US$)", s."Cotação (em R$)", 
            s.num_parcela, s.total_parcelas
        FROM staging_transacoes s
        JOIN dim_data d ON s."Data de Compra" = d.data
        JOIN dim_titular t ON s."Nome no Cartão" = t.nome_titular
        JOIN dim_categoria c ON s."Categoria" = c.nome_categoria
        JOIN dim_estabelecimento e ON s."Descrição" = e.nome_estabelecimento;
    """))

print("ETL executado com sucesso!")