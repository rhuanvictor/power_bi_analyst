import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Configurar a página para usar um layout mais amplo
st.set_page_config(page_title="Análise Financeira", layout='wide')


# URL do arquivo no GitHub (use o link raw)
url = "https://raw.githubusercontent.com/rhuanvictor/power_bi_analyst/main/Financial%20Sample.xlsx"

# Ler o arquivo Excel diretamente do GitHub
try:
    df = pd.read_excel(url, sheet_name='Sheet1')
    st.write(df)
except Exception as e:
    st.error(f"Erro ao carregar o arquivo: {e}")

# Remover espaços nos nomes das colunas
df.columns = df.columns.str.strip()

# --- Seção 1: Lucro por Segmento ---
# Processar os dados: agrupar por Segment e somar o Profit
df_grouped_profit = df.groupby('Segment')['Profit'].sum().reset_index()

# Filtrar para considerar apenas valores positivos para o gráfico e a tabela
df_positive_profit = df_grouped_profit[df_grouped_profit['Profit'] > 0]



# Criar o gráfico de pizza usando Plotly com formatação de dólar
fig_profit = px.pie(df_positive_profit, names='Segment', values='Profit', title='Profit by Segment')

# Personalizar o formato para exibir valores em dólares
fig_profit.update_traces(textposition='inside', textinfo='percent+label',
                          hovertemplate='%{label}: $%{value:,.2f}<extra></extra>')

# Exibir o gráfico no Streamlit
st.title('Lucro por Segmento (em Dólares)')
st.plotly_chart(fig_profit)
# Exibir a soma total do lucro considerando apenas valores positivos
total_profit = df_positive_profit['Profit'].sum()
st.write(f"Soma Total do Lucro (considerando apenas valores positivos): ${total_profit:,.2f}")

# Calcular porcentagem para cada segmento
df_positive_profit['Percentage'] = (df_positive_profit['Profit'] / total_profit) * 100

# Exibir a tabela com porcentagens e lucros
st.write("### Tabela de Lucro e Porcentagem por Segmento")
st.table(df_positive_profit[['Segment', 'Profit', 'Percentage']].style.format({
    'Profit': '${:,.2f}',  # Formatação em dólar
    'Percentage': '{:.2f}%'  # Formatação em porcentagem
}))


# --- Seção 2: Mapa de Vendas por País ---
# Inicializar o tamanho do círculo se não estiver na sessão
if 'circle_size' not in st.session_state:
    st.session_state.circle_size = 30  # Tamanho inicial do círculo

# Função para aumentar o tamanho do círculo
def increase_circle_size():
    st.session_state.circle_size += 5  # Aumenta o tamanho do círculo

# Função para diminuir o tamanho do círculo
def decrease_circle_size():
    st.session_state.circle_size = max(5, st.session_state.circle_size - 5)  # Diminui o tamanho do círculo, com limite mínimo

# Verificar se as colunas existem
if 'Sales' in df.columns and 'Units Sold' in df.columns:
    # Agrupar os dados por país, somando 'Sales' e 'Units Sold'
    df_grouped_sales = df.groupby('Country').agg({'Sales': 'sum', 'Units Sold': 'sum'}).reset_index()

    # Normalizar os tamanhos dos círculos com um intervalo definido
    min_sales = df_grouped_sales['Sales'].min()
    max_sales = df_grouped_sales['Sales'].max()

    # Definindo a faixa de tamanhos para os círculos
    min_circle_size = 5
    max_circle_size = 50

    # Normalizar o tamanho dos círculos
    df_grouped_sales['Bubble Size'] = np.interp(df_grouped_sales['Sales'], 
                                                 (min_sales, max_sales), 
                                                 (min_circle_size, max_circle_size))

    # Criar o gráfico de mapa utilizando Plotly Express
    fig_sales = px.scatter_geo(df_grouped_sales, 
                                locations="Country", 
                                locationmode='country names', 
                                size="Bubble Size",  # O tamanho do círculo será baseado no tamanho normalizado
                                color="Units Sold",  # A cor será baseada nas unidades vendidas
                                hover_name="Country", 
                                hover_data={"Sales": ':,.2f', "Units Sold": True},
                                title="Soma de Sales e Units Sold por Country")

   
    # Adicionar a chave do Bing Maps e configurar a camada de mapa
    fig_sales.update_layout(
        geo=dict(
            showframe=False, 
            showcoastlines=True, 
            projection_type='natural earth',
            visible=False,
            resolution=50,
            showland=True,
            showlakes=True,
            subunitcolor='white',
            landcolor='rgb(217, 217, 217)',
            countrycolor='rgb(217, 217, 217)',
            lakecolor='rgb(255, 255, 255)',
            projection=dict(type='mercator'),
            scope='world',
            domain=dict(x=[0, 1], y=[0, 1])  # Faz o mapa ocupar toda a área horizontalmente
        ),
        width=1500,  # Aumenta a largura do gráfico
        height=800   # Define uma altura maior para o gráfico
    )

    # Exibir o gráfico no Streamlit dentro de um container
    with st.container():
        st.title("Mapa: Soma de Sales e Units Sold por Country")
        st.plotly_chart(fig_sales, use_container_width=True)

    # Exibir os dados resumidos em uma tabela
    st.write("### Tabela de Soma de Sales e Units Sold por Country")
    st.table(df_grouped_sales.style.format({
        'Sales': '${:,.2f}',  # Formatação para o campo de vendas
        'Units Sold': '{:,.0f}'  # Formatação para o campo de unidades vendidas
    }))
    
    # --- Seção 3: Gráfico de Bolha de Profit por País ---
    # Agrupar os dados por país, somando 'Profit'
    df_grouped_profit_country = df.groupby('Country')['Profit'].sum().reset_index()

    # Normalizar os tamanhos dos círculos para o gráfico de Profit
    min_profit = df_grouped_profit_country['Profit'].min()
    max_profit = df_grouped_profit_country['Profit'].max()

    # Normalizar o tamanho dos círculos com uma faixa definida
    df_grouped_profit_country['Bubble Size'] = np.interp(df_grouped_profit_country['Profit'], 
                                                          (min_profit, max_profit), 
                                                          (min_circle_size, max_circle_size))

    # Criar o gráfico de bolhas para a soma do lucro por país
    fig_profit_country = px.scatter_geo(df_grouped_profit_country, 
                                         locations="Country", 
                                         locationmode='country names', 
                                         size="Bubble Size",  # O tamanho do círculo será baseado no lucro
                                         color="Profit",  # A cor será baseada no lucro
                                         hover_name="Country", 
                                         hover_data={"Profit": ':,.2f'},
                                         title="Soma de Profit por Country")

    # Atualizar layout para o gráfico de Profit
    fig_profit_country.update_layout(
        geo=dict(
            showframe=False, 
            showcoastlines=True, 
            projection_type='natural earth',
            visible=False,
            resolution=50,
            showland=True,
            showlakes=True,
            subunitcolor='white',
            landcolor='rgb(217, 217, 217)',
            countrycolor='rgb(217, 217, 217)',
            lakecolor='rgb(255, 255, 255)',
            projection=dict(type='mercator'),
            scope='world',
            domain=dict(x=[0, 1], y=[0, 1])  # Faz o mapa ocupar toda a área horizontalmente
        ),
        width=1500,  # Aumenta a largura do gráfico
        height=800   # Define uma altura maior para o gráfico
    )

    # Exibir o gráfico de lucro por país
    st.title("Mapa: Soma de Profit por Country")
    st.plotly_chart(fig_profit_country, use_container_width=True)

else:
    st.write("Colunas 'Sales' e/ou 'Units Sold' não encontradas.")
