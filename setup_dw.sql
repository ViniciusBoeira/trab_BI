CREATE TABLE dim_data (id_data INTEGER PRIMARY KEY, data DATE, dia INTEGER, mes INTEGER, ano INTEGER, trimestre INTEGER, dia_semana TEXT);
CREATE TABLE dim_titular (id_titular INTEGER PRIMARY KEY, nome_titular TEXT, final_cartao INTEGER);
CREATE TABLE dim_categoria (id_categoria INTEGER PRIMARY KEY, nome_categoria TEXT);
CREATE TABLE dim_estabelecimento (id_estabelecimento INTEGER PRIMARY KEY, nome_estabelecimento TEXT);
CREATE TABLE fato_transacao (
    id_data INTEGER, id_titular INTEGER, id_categoria INTEGER, id_estabelecimento INTEGER,
    valor_brl REAL, valor_usd REAL, cotacao REAL, num_parcela INTEGER, total_parcelas INTEGER
);