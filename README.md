Plano do Projeto

Objetivo: Construir um ecossistema de Business Intelligence para análise de gastos de cartões de crédito, utilizando dados de 12 meses de faturas.

Fases de Execução:

Mapeamento de Dados: Análise de 12 arquivos CSV com estrutura de faturas bancárias.

Modelagem Dimensional: Criação de um esquema em estrela (Star Schema) para otimizar a performance analítica.

Desenvolvimento do Pipeline ETL: * Extração: Leitura automatizada via Python e Pandas.

Transformação: Limpeza de campos nulos, padronização de tipos de dados (Datas e Floats) e decomposição de parcelas (ex: "2/10").

Carga: Ingestão para PostgreSQL com orquestração de chaves substitutas (IDs).

Análise e Validação: Execução de consultas SQL para responder métricas de negócio (Gasto por titular, categoria e tempo).



Arquitetura do Data Warehouse

Modelo: Star Schema (Esquema em Estrela)

Tabela Fato (fato_transacao): Armazena os eventos quantitativos (valor em R$, valor em US$, cotação e número da parcela) e as chaves estrangeiras (FKs).

Dimensões:

dim_data: Atributos temporais (dia, mês, ano, trimestre).

dim_titular: Nome do dono do cartão e final do cartão.

dim_categoria: Classificações de despesas (ex: Restaurante, Saúde).

dim_estabelecimento: Descrição do local da transação.



Dicionário de Dados

Este documento descreve a estrutura do seu Data Warehouse para garantir a clareza do modelo:

<img width="585" height="233" alt="image" src="https://github.com/user-attachments/assets/bea1863b-16c0-4d17-bfe9-e366f9824a5a" />



Como Executar

Crie o banco de dados no PostgreSQL e execute o script `setup_dw.sql`.
Instale as dependências: `pip install pandas sqlalchemy psycopg2`.
Coloque os CSVs na pasta `/dados`.
Execute o script: `python etl.py`.



Resultados do banco de dados:

<img width="491" height="475" alt="image" src="https://github.com/user-attachments/assets/b00c5166-55a3-4dfd-a1a4-80fd3f3186da" />

<img width="596" height="478" alt="image" src="https://github.com/user-attachments/assets/31e69ecc-d9c1-430a-a1a9-e9695a302615" />

<img width="588" height="500" alt="image" src="https://github.com/user-attachments/assets/dd7c6271-b139-4331-840b-edc74de9c42b" />

<img width="722" height="346" alt="image" src="https://github.com/user-attachments/assets/0399d044-0398-4f4c-86e5-fe00cf31a7b3" />

<img width="858" height="475" alt="image" src="https://github.com/user-attachments/assets/9ccde8fc-ac90-4935-9b88-8e03660923e8" />

Perguntas de Negócio:

<img width="561" height="499" alt="image" src="https://github.com/user-attachments/assets/ed3270bd-6b40-4897-ac95-3239b05482ed" />

<img width="700" height="501" alt="image" src="https://github.com/user-attachments/assets/682f9292-57f9-44dc-a91f-ca154cc60f76" />

<img width="755" height="334" alt="image" src="https://github.com/user-attachments/assets/10b5c921-297e-49f6-9d53-90f8b4f655c9" />

<img width="726" height="367" alt="image" src="https://github.com/user-attachments/assets/df2e94a0-941e-426d-8c8c-3f7e3c88494b" />

<img width="802" height="307" alt="image" src="https://github.com/user-attachments/assets/a6f18ee9-e132-4b26-b9b1-fb1c87d4bfcd" />

(Star Schema)

```mermaid
erDiagram

    DIM_DATA {
        INTEGER id_data PK
        DATE data
        INTEGER dia
        INTEGER mes
        INTEGER ano
        INTEGER trimestre
        TEXT dia_semana
    }

    DIM_TITULAR {
        INTEGER id_titular PK
        TEXT nome_titular
        INTEGER final_cartao
    }

    DIM_CATEGORIA {
        INTEGER id_categoria PK
        TEXT nome_categoria
    }

    DIM_ESTABELECIMENTO {
        INTEGER id_estabelecimento PK
        TEXT nome_estabelecimento
    }

    FATO_TRANSACAO {
        INTEGER id_data FK
        INTEGER id_titular FK
        INTEGER id_categoria FK
        INTEGER id_estabelecimento FK
        REAL valor_brl
        REAL valor_usd
        REAL cotacao
        INTEGER num_parcela
        INTEGER total_parcelas
    }

    DIM_DATA ||--o{ FATO_TRANSACAO : possui
    DIM_TITULAR ||--o{ FATO_TRANSACAO : possui
    DIM_CATEGORIA ||--o{ FATO_TRANSACAO : possui
    DIM_ESTABELECIMENTO ||--o{ FATO_TRANSACAO : possui
```








