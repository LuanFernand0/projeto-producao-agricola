import streamlit as st
import pandas as pd
import plotly.express as px
import json
import urllib.request

st.set_page_config(page_title="Produção Agrícola Brasil", layout="wide", page_icon="🌾")

st.title("🌾 Análise de Produção Agrícola no Brasil (2015-2024)")
st.markdown("""
- **Aluno:** Luan Fernando Oliveira Pedrosa  
- **Curso:** Sistemas de Informação — Centro Universitário La Salle (Unilasalle-RJ)  
- **Professor:** Alexandre Neves Louzada  
- **Disciplina:** Linguagem de Programação — Análise e Visualização de Dados com Python  
""")
st.markdown("---")

@st.cache_data
def carregar_dados():
    return pd.read_csv("dados/simulacao_producao_agricola_brasil.csv")

@st.cache_data
def carregar_geojson():
    url = 'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson'
    try:
        with urllib.request.urlopen(url) as response:
            return json.load(response)
    except:
        return None

df = carregar_dados()
brazil_geo = carregar_geojson()

st.sidebar.header("Filtros Dinâmicos")

ano_min, ano_max = int(df['ano'].min()), int(df['ano'].max())
ano_selecionado = st.sidebar.slider("Período (Ano)", ano_min, ano_max, (ano_min, ano_max))

regioes = df['regiao'].unique().tolist()
regiao_selecionada = st.sidebar.multiselect("Região", regioes, default=regioes)

coluna_estado = 'estado' if 'estado' in df.columns else 'uf'
estados = df[df['regiao'].isin(regiao_selecionada)][coluna_estado].unique().tolist()
estado_selecionado = st.sidebar.multiselect("Estado", estados, default=estados)

culturas = df['cultura'].unique().tolist()
cultura_selecionada = st.sidebar.multiselect("Cultura", culturas, default=culturas)

df_filtrado = df[
    (df['ano'] >= ano_selecionado[0]) & (df['ano'] <= ano_selecionado[1]) &
    (df['regiao'].isin(regiao_selecionada)) &
    (df[coluna_estado].isin(estado_selecionado)) &
    (df['cultura'].isin(cultura_selecionada))
]

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

aba1, aba2, aba3, aba4, aba5 = st.tabs(["Evolução e Regional", "Culturas e Plantio", "Correlações e Heatmap", "Mapa Interativo", "Tabela de Dados"])

with aba1:
    st.subheader("Evolução Temporal da Produção")
    df_tempo = df_filtrado.groupby('ano')['producao_toneladas'].sum().reset_index()
    fig_linha = px.line(df_tempo, x='ano', y='producao_toneladas', markers=True, title="Produção Total por Ano (t)")
    st.plotly_chart(fig_linha, use_container_width=True)

    st.subheader("Comparação Regional (Por Estado)")
    df_estado = df_filtrado.groupby(coluna_estado)['producao_toneladas'].sum().reset_index().sort_values('producao_toneladas', ascending=False)
    fig_bar_est = px.bar(df_estado, x=coluna_estado, y='producao_toneladas', color='producao_toneladas', color_continuous_scale='Greens', title="Produção por Estado")
    st.plotly_chart(fig_bar_est, use_container_width=True)

with aba2:
    st.subheader("Produtividade por Cultura")
    df_cultura = df_filtrado.groupby('cultura')['produtividade'].mean().reset_index()
    fig_cultura = px.bar(df_cultura, x='cultura', y='produtividade', color='cultura', title="Produtividade Média (t/ha)")
    st.plotly_chart(fig_cultura, use_container_width=True)

    colA, colB = st.columns(2)
    with colA:
        st.subheader("Distribuição do Valor Econômico")
        fig_box = px.box(df_filtrado, x='regiao', y='valor_producao', color='cultura', title="Valor Econômico por Região e Cultura")
        st.plotly_chart(fig_box, use_container_width=True)
    with colB:
        st.subheader("Proporção de Área Plantada")
        df_pizza = df_filtrado.groupby('cultura')['area_plantada_ha'].sum().reset_index()
        fig_pizza = px.pie(df_pizza, names='cultura', values='area_plantada_ha', hole=0.4, title="Área Plantada por Cultura")
        st.plotly_chart(fig_pizza, use_container_width=True)

with aba3:
    col_x = 'volume_chuvas' if 'volume_chuvas' in df_filtrado.columns else 'area_plantada_ha'
    title_x = "Volume de Chuvas x Produtividade" if col_x == 'volume_chuvas' else "Área Plantada x Produção"
    y_col = 'produtividade' if col_x == 'volume_chuvas' else 'producao_toneladas'
    
    st.subheader(f"Relação: {title_x}")
    fig_scatter = px.scatter(df_filtrado, x=col_x, y=y_col, color='regiao', opacity=0.7, title=title_x)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.subheader("Mapa de Calor (Heatmap): Ano vs Região")
    if not df_filtrado.empty:
        heatmap_data = df_filtrado.pivot_table(values='producao_toneladas', index='ano', columns='regiao', aggfunc='sum')
        fig_heat = px.imshow(heatmap_data, text_auto=".2s", color_continuous_scale='Greens', aspect='auto', title="Evolução da Produção por Região")
        st.plotly_chart(fig_heat, use_container_width=True)

with aba4:
    st.subheader("Mapa Interativo de Produção por Estado")
    
    if brazil_geo and not df_filtrado.empty:
        df_mapa = df_filtrado.groupby(coluna_estado)['producao_toneladas'].sum().reset_index()
        
        fig_mapa = px.choropleth(
            df_mapa,
            geojson=brazil_geo,
            locations=coluna_estado,
            featureidkey='properties.sigla',
            color='producao_toneladas',
            color_continuous_scale='Greens',
            title='Produção Agrícola Total por Estado (t)',
            hover_name=coluna_estado
        )
        fig_mapa.update_geos(fitbounds="locations", visible=False)
        fig_mapa.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig_mapa, use_container_width=True)
    else:
        st.warning("Aguarde o carregamento do mapa ou ajuste os filtros.")

with aba5:
    st.subheader("Exploração Detalhada (Tabela Dinâmica)")
    st.dataframe(df_filtrado)

st.markdown("---")
st.markdown("### Conclusão Executiva")
st.markdown("A análise confirma que a produção agrícola está concentrada em regiões específicas, com forte dependência de fatores climáticos e área plantada. O uso de visualizações geográficas interativas e análises cruzadas permite identificar gargalos produtivos e orientar investimentos estratégicos no setor agrário nacional.")
