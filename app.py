import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Produção Agrícola Brasil", layout="wide")

@st.cache_data
def carregar_dados():
    df = pd.read_csv('dados/simulacao_producao_agricola_brasil.csv')
    df['ano'] = df['ano'].astype(int)
    return df

try:
    df = carregar_dados()
except:
    st.error("Erro ao carregar o arquivo CSV. Certifique-se de que a pasta 'dados' com o arquivo 'simulacao_producao_agricola_brasil.csv' está presente no repositório.")
    st.stop()

st.title("🌾 Análise de Produção Agrícola no Brasil (2015-2024)")
st.markdown("**Aluno:** Luan Fernando Oliveira Pedrosa | **Professor:** Alexandre Neves Louzada")
st.markdown(" Análise e Visualização de Dados.")

st.sidebar.header("Filtros Dinâmicos")
anos = st.sidebar.slider("Período (Ano)", int(df['ano'].min()), int(df['ano'].max()), (int(df['ano'].min()), int(df['ano'].max())))
regioes = st.sidebar.multiselect("Região", df['regiao'].unique())
estados = st.sidebar.multiselect("Estado", df['uf'].unique())
culturas = st.sidebar.multiselect("Cultura", df['cultura'].unique())

df_filtrado = df[(df['ano'] >= anos[0]) & (df['ano'] <= anos[1])]
if regioes:
    df_filtrado = df_filtrado[df_filtrado['regiao'].isin(regioes)]
if estados:
    df_filtrado = df_filtrado[df_filtrado['uf'].isin(estados)]
if culturas:
    df_filtrado = df_filtrado[df_filtrado['cultura'].isin(culturas)]
    
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

prod_total = f"{df_filtrado['producao_toneladas'].sum():,.0f}".replace(',', '.')
val_econ = f"R$ {df_filtrado['valor_producao'].sum():,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
area_plant = f"{df_filtrado['area_plantada_ha'].sum():,.0f}".replace(',', '.')
prod_media = f"{df_filtrado['produtividade'].mean():,.2f}".replace('.', ',')

col1.metric("Produção Total", f"{prod_total} t")
col2.metric("Valor Econômico", val_econ)
col3.metric("Área Plantada", f"{area_plant} ha")
col4.metric("Produtividade Média", f"{prod_media} t/ha")

st.markdown("---")
tab1, tab2, tab3 = st.tabs(["Evolução e Regional", "Culturas e Clima", "Base de Dados e Conclusão"])

with tab1:
    st.subheader("Evolução Temporal da Produção")
    fig_tempo = px.line(df_filtrado.groupby('ano')['producao_toneladas'].sum().reset_index(), 
                        x='ano', y='producao_toneladas', markers=True, title="Produção Total por Ano (Toneladas)")
    st.plotly_chart(fig_tempo, use_container_width=True)
    
    st.subheader("Comparação por Estado (UF)")
    fig_est = px.bar(df_filtrado.groupby('uf')['producao_toneladas'].sum().reset_index(), 
                     x='uf', y='producao_toneladas', color='uf', title="Volume Produzido por Estado")
    st.plotly_chart(fig_est, use_container_width=True)

with tab2:
    st.subheader("Produção por Cultura Agrícola")
    fig_cultura = px.bar(df_filtrado.groupby('cultura')['producao_toneladas'].sum().reset_index(), 
                         x='cultura', y='producao_toneladas', color='cultura', title="Desempenho por Tipo de Cultura")
    st.plotly_chart(fig_cultura, use_container_width=True)
    
    st.subheader("Correlação: Volume de Chuvas x Produtividade")
    fig_disp = px.scatter(df_filtrado, x='chuva_mm', y='produtividade', color='cultura', 
                          title="Impacto das Precipitações na Produtividade (t/ha)")
    st.plotly_chart(fig_disp, use_container_width=True)

with tab3:
    st.subheader("Exploração da Base de Dados Filtrada")
    st.dataframe(df_filtrado, use_container_width=True)
    
    st.subheader("Interpretação e Conclusão Executiva")
    st.markdown("""
    * **Padrões Identificados:** A análise demonstrou oscilações importantes ao longo dos anos, com destaque para as culturas de maior expressão econômica e de maior volume.
    * **Impacto Climático:** O gráfico de dispersão evidencia que o volume de chuvas afeta diretamente a eficiência e a produtividade por hectare.
    * **Conclusão:** O projeto cumpre os objetivos propostos na G1, evidenciando a importância do uso de ferramentas analíticas para a tomada de decisões no agronegócio brasileiro.
    """)
