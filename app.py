import streamlit as st
import pandas as pd
import plotly.express as px
import json
import urllib.request

st.set_page_config(page_title="Evasão Escolar Brasil", layout="wide", page_icon="🏫")

st.title("🏫 Análise de Evasão Escolar no Ensino Médio Brasileiro (2015-2024)")
st.markdown("""
- **Aluno:** Miguel Soares Marreiros  
- **Curso:** Sistemas de Informação — Centro Universitário La Salle (Unilasalle-RJ)  
- **Professor:** Alexandre Neves Louzada  
- **Disciplina:** Linguagem de Programação — Análise e Visualização de Dados com Python  
""")
st.markdown("---")

@st.cache_data
def carregar_dados():
    return pd.read_csv("dados/simulacao_evasao_escolar_brasil.csv")

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
ano_selecionado = st.sidebar.slider("Ano", ano_min, ano_max, (ano_min, ano_max))

regioes = df['regiao'].unique().tolist()
regiao_selecionada = st.sidebar.multiselect("Região", regioes, default=regioes)

estados = df[df['regiao'].isin(regiao_selecionada)]['uf'].unique().tolist()
estado_selecionado = st.sidebar.multiselect("Estado", estados, default=estados)

redes = df['rede_ensino'].unique().tolist()
rede_selecionada = st.sidebar.multiselect("Rede de Ensino", redes, default=redes)

series = df['serie'].unique().tolist()
serie_selecionada = st.sidebar.multiselect("Série do Ensino Médio", series, default=series)

riscos = df['nivel_risco'].unique().tolist()
risco_selecionado = st.sidebar.multiselect("Nível de Risco", riscos, default=riscos)

df_filtrado = df[
    (df['ano'] >= ano_selecionado[0]) & (df['ano'] <= ano_selecionado[1]) &
    (df['regiao'].isin(regiao_selecionada)) &
    (df['uf'].isin(estado_selecionado)) &
    (df['rede_ensino'].isin(rede_selecionada)) &
    (df['serie'].isin(serie_selecionada)) &
    (df['nivel_risco'].isin(risco_selecionado))
]

col1, col2, col3, col4, col5 = st.columns(5)

taxa_media = df_filtrado['taxa_evasao'].mean()
total_evasoes = df_filtrado['evasoes'].sum()

estado_critico = df_filtrado.groupby('uf')['taxa_evasao'].mean().idxmax() if not df_filtrado.empty else "N/A"
rede_critica = df_filtrado.groupby('rede_ensino')['taxa_evasao'].mean().idxmax() if not df_filtrado.empty else "N/A"
serie_critica = df_filtrado.groupby('serie')['taxa_evasao'].mean().idxmax() if not df_filtrado.empty else "N/A"

col1.metric("Taxa Média de Evasão", f"{taxa_media:.2f}%")
col2.metric("Total de Evasões", f"{total_evasoes:,.0f}".replace(',', '.'))
col3.metric("Estado + Crítico", estado_critico)
col4.metric("Rede + Afetada", rede_critica)
col5.metric("Série + Crítica", serie_critica)

st.markdown("---")

aba1, aba2, aba3, aba4, aba5 = st.tabs(["Evolução e Regional", "Escolaridade e Risco", "Correlações e Heatmap", "Mapa Interativo", "Tabela de Dados"])

with aba1:
    st.subheader("Evolução Temporal da Evasão")
    df_tempo = df_filtrado.groupby('ano')['taxa_evasao'].mean().reset_index()
    fig_linha = px.line(df_tempo, x='ano', y='taxa_evasao', markers=True, title="Taxa Média de Evasão por Ano")
    st.plotly_chart(fig_linha, use_container_width=True)

    st.subheader("Comparação Regional (Por Estado)")
    df_estado = df_filtrado.groupby('uf')['taxa_evasao'].mean().reset_index().sort_values('taxa_evasao', ascending=False)
    fig_bar_est = px.bar(df_estado, x='uf', y='taxa_evasao', color='taxa_evasao', color_continuous_scale='Reds', title="Evasão por Estado")
    st.plotly_chart(fig_bar_est, use_container_width=True)

with aba2:
    st.subheader("Evasão por Série do Ensino Médio")
    df_serie = df_filtrado.groupby('serie')['taxa_evasao'].mean().reset_index()
    fig_serie = px.bar(df_serie, x='serie', y='taxa_evasao', color='serie', title="Taxa de Abandono por Série")
    st.plotly_chart(fig_serie, use_container_width=True)

    colA, colB = st.columns(2)
    with colA:
        st.subheader("Distribuição por Nível de Risco")
        fig_rede = px.box(df_filtrado, x='rede_ensino', y='taxa_evasao', color='nivel_risco', title="Evasão por Rede e Risco")
        st.plotly_chart(fig_rede, use_container_width=True)
    with colB:
        st.subheader("Proporção por Rede de Ensino")
        df_pizza = df_filtrado.groupby('rede_ensino')['evasoes'].sum().reset_index()
        fig_pizza = px.pie(df_pizza, names='rede_ensino', values='evasoes', hole=0.4, title="Total de Evasões (Pública vs Privada)")
        st.plotly_chart(fig_pizza, use_container_width=True)

with aba3:
    st.subheader("Relação: Renda Familiar x Taxa de Evasão")
    fig_scatter = px.scatter(df_filtrado, x='renda_media_familiar', y='taxa_evasao', color='regiao', opacity=0.7, 
                             title="Impacto da Renda na Evasão (Dispersão)", trendline="ols")
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.subheader("Mapa de Calor (Heatmap): Ano vs Região")
    if not df_filtrado.empty:
        heatmap_data = df_filtrado.pivot_table(values='taxa_evasao', index='ano', columns='regiao', aggfunc='mean')
        fig_heat = px.imshow(heatmap_data, text_auto=".2f", color_continuous_scale='Oranges', aspect='auto', title="Evolução da Evasão por Região ao Longo do Tempo")
        st.plotly_chart(fig_heat, use_container_width=True)
    
    st.markdown("**Interpretação Textual:** Gráficos de dispersão mostram que regiões com menor renda familiar média apresentam taxas de evasão mais acentuadas. O Mapa de Calor permite identificar rapidamente em que anos específicos cada região atingiu o seu pico crítico de abandono.")

with aba4:
    st.subheader("Mapa Interativo de Evasão por Estado")
    st.markdown("Visualização geográfica das taxas médias de evasão em todo o território nacional. Estados com cores mais escuras representam maiores taxas de abandono.")
    
    if brazil_geo and not df_filtrado.empty:
        df_mapa = df_filtrado.groupby('uf')['taxa_evasao'].mean().reset_index()
        
        fig_mapa = px.choropleth(
            df_mapa,
            geojson=brazil_geo,
            locations='uf',
            featureidkey='properties.sigla',
            color='taxa_evasao',
            color_continuous_scale='Reds',
            title='Taxa de Evasão Escolar por Estado (%)',
            hover_name='uf'
        )
        fig_mapa.update_geos(fitbounds="locations", visible=False)
        fig_mapa.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig_mapa, use_container_width=True)
    else:
        st.warning("Selecione pelo menos um estado nos filtros para visualizar o mapa ou aguarde o carregamento das coordenadas geográficas.")

with aba5:
    st.subheader("Exploração Detalhada (Tabela Dinâmica)")
    st.dataframe(df_filtrado)

st.markdown("---")
st.markdown("### Conclusão Executiva")
st.markdown("""
A análise dos dados revela que a evasão no Ensino Médio está fortemente atrelada a indicadores socioeconômicos e estruturais.
A rede pública e o primeiro ano do Ensino Médio costumam apresentar as taxas mais críticas de abandono, especialmente em estados 
sinalizados com cores mais quentes no mapa interativo. Políticas públicas focadas em complementação de renda, 
melhoria da infraestrutura e suporte ao aluno logo no ingresso do ensino médio podem mitigar drasticamente estes números.
""")
