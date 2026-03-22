import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

#Conexão com o Banco de Dados
engine = create_engine("postgresql+psycopg2://postgres:root@localhost:5432/BI")

#Configuração da Página
st.set_page_config(page_title="Analytics Cartão de Crédito", layout="wide", page_icon="💳")

#ESTILIZAÇÃO CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    [data-testid="stMetricValue"] {
        font-size: 28px;
    }
    </style>
    """, unsafe_allow_html=True)

#FILTROS
st.sidebar.header("🔍 Filtros de Análise")

#Buscar anos e titulares para os filtros
anos_df = pd.read_sql("SELECT DISTINCT ano FROM dim_data ORDER BY ano DESC", engine)
titulares_df = pd.read_sql("SELECT DISTINCT nome_titular FROM dim_titular", engine)

ano_selecionado = st.sidebar.multiselect("Selecione o Ano", 
                                       options=anos_df['ano'].tolist(),
                                       default=anos_df['ano'].tolist())

titular_selecionado = st.sidebar.multiselect("Selecione o Titular", 
                                           options=titulares_df['nome_titular'].tolist(),
                                           default=titulares_df['nome_titular'].tolist())

#Proteção para caso o usuário desmarque todos os filtros
if not ano_selecionado or not titular_selecionado:
    st.warning("⚠️ Por favor, selecione ao menos um Ano e um Titular no menu lateral.")
    st.stop()

#Lógica de Filtro SQL
filtro_sql = f"""
    WHERE d.ano IN ({','.join(map(str, ano_selecionado))})
    AND t.nome_titular IN ({str(titular_selecionado)[1:-1]})
"""

#TÍTULO
st.title("📊 BI: Gestão de Transações")
st.markdown("---")

#CABEÇALHO COM MÉTRICAS
total_geral = pd.read_sql(f"""
    SELECT SUM(f.valor_brl) as total, COUNT(*) as qtd 
    FROM fato_transacao f 
    JOIN dim_data d ON f.id_data = d.id_data
    JOIN dim_titular t ON f.id_titular = t.id_titular
    {filtro_sql}""", engine)

m1, m2, m3 = st.columns(3)
with m1:
    valor = total_geral['total'][0] if total_geral['total'][0] else 0
    st.metric("Gasto Total", f"R$ {valor:,.2f}")
with m2:
    qtd = total_geral['qtd'][0] if total_geral['qtd'][0] else 0
    st.metric("Total de Transações", f"{qtd} un")
with m3:
    ticket = valor / qtd if qtd > 0 else 0
    st.metric("Ticket Médio", f"R$ {ticket:,.2f}")

st.markdown("###")

#EVOLUÇÃO E CATEGORIAS
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Evolução Mensal de Gastos")
    df_evolucao = pd.read_sql(f"""
        SELECT d.ano || '-' || LPAD(CAST(d.mes AS TEXT), 2, '0') as periodo, SUM(f.valor_brl) as total
        FROM fato_transacao f JOIN dim_data d ON f.id_data = d.id_data
        JOIN dim_titular t ON f.id_titular = t.id_titular
        {filtro_sql} GROUP BY d.ano, d.mes ORDER BY d.ano, d.mes""", engine)
    if not df_evolucao.empty:
        st.area_chart(df_evolucao.set_index('periodo'))

with col2:
    st.subheader("🍴 Top 10 Categorias")
    df_categoria = pd.read_sql(f"""
        SELECT c.nome_categoria, SUM(f.valor_brl) as total
        FROM fato_transacao f JOIN dim_categoria c ON f.id_categoria = c.id_categoria
        JOIN dim_data d ON f.id_data = d.id_data
        JOIN dim_titular t ON f.id_titular = t.id_titular
        {filtro_sql} GROUP BY 1 ORDER BY 2 DESC LIMIT 10""", engine)
    if not df_categoria.empty:
        st.bar_chart(df_categoria.set_index('nome_categoria'))

st.markdown("---")

#ESTABELECIMENTOS E PARCELAMENTO
col3, col4 = st.columns(2)

with col3:
    st.subheader("🏪 Top 5 Estabelecimentos")
    df_estab = pd.read_sql(f"""
        SELECT e.nome_estabelecimento as Local, SUM(f.valor_brl) as "Total Gasto (R$)"
        FROM fato_transacao f JOIN dim_estabelecimento e ON f.id_estabelecimento = e.id_estabelecimento
        JOIN dim_data d ON f.id_data = d.id_data
        JOIN dim_titular t ON f.id_titular = t.id_titular
        {filtro_sql} GROUP BY 1 ORDER BY 2 DESC LIMIT 5""", engine)
    st.dataframe(df_estab, use_container_width=True, hide_index=True)

with col4:
    st.subheader("💳 Proporção À Vista vs Parcelado")
    df_parcelas = pd.read_sql(f"""
        SELECT CASE WHEN total_parcelas > 1 THEN 'Parcelado' ELSE 'À Vista' END as tipo,
               COUNT(*) as qtd
        FROM fato_transacao f
        JOIN dim_data d ON f.id_data = d.id_data
        JOIN dim_titular t ON f.id_titular = t.id_titular
        {filtro_sql} GROUP BY 1""", engine)
    if not df_parcelas.empty:
        st.bar_chart(df_parcelas.set_index('tipo'))

st.caption("Desenvolvido para o Trabalho de Cartões de Crédito de BI - CC")