-- 1. Valor total gasto por mês
SELECT d.mes, d.ano, SUM(f.valor_brl) as total_gasto
FROM fato_transacao f
JOIN dim_data d ON f.id_data = d.id_data
GROUP BY d.ano, d.mes
ORDER BY d.ano, d.mes;

-- 2. Gastos distribuídos por categoria (Top 10)
SELECT c.nome_categoria, SUM(f.valor_brl) as total_categoria
FROM fato_transacao f
JOIN dim_categoria c ON f.id_categoria = c.id_categoria
GROUP BY c.nome_categoria
ORDER BY total_categoria DESC
LIMIT 10;

-- 3. Total de gastos por titular do cartão
SELECT t.nome_titular, t.final_cartao, SUM(f.valor_brl) as total_gasto
FROM fato_transacao f
JOIN dim_titular t ON f.id_titular = t.id_titular
GROUP BY t.nome_titular, t.final_cartao;

-- 4. Estabelecimentos com maior volume de gastos
SELECT e.nome_estabelecimento, SUM(f.valor_brl) as total_gasto
FROM fato_transacao f
JOIN dim_estabelecimento e ON f.id_estabelecimento = e.id_estabelecimento
GROUP BY e.nome_estabelecimento
ORDER BY total_gasto DESC
LIMIT 5;

-- 5. Proporção de compras parceladas vs à vista
SELECT 
    CASE WHEN total_parcelas > 1 THEN 'Parcelado' ELSE 'À Vista' END as tipo_compra,
    COUNT(*) as qtd_transacoes,
    SUM(valor_brl) as total_valor
FROM fato_transacao
GROUP BY tipo_compra;