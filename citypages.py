import dash
from dash import html, dcc, Input, Output
import pandas as pd
from urllib.parse import unquote
import numpy as np

## 1. Função de Carregamento de Dados Otimizada
def load_data():
    # Carrega sem conversão inicial para identificar problemas
    df = pd.read_csv('ibge.txt')
    
    # Lista de colunas e seus tipos esperados
    columns_spec = {
        'Município [-]': 'category',
        'Código [-]': 'str',
        'Gentílico [-]': 'category',
        'Prefeito [2025]': 'category',
        'Área Territorial - km² [2024]': 'float32',
        'População no último censo - pessoas [2022]': 'float32',
        'Densidade demográfica - hab/km² [2022]': 'float32',
        'População estimada - pessoas [2024]': 'float32',
        'IDHM (Índice de desenvolvimento humano municipal) [2010]': 'float32',
        'PIB per capita - R$ [2021]': 'float32',
        'Total de receitas brutas realizadas - R$ [2024]': 'float64',
        'Total de despesas brutas empenhadas - R$ [2024]': 'float64'
    }
    
    # Converte colunas gradualmente com tratamento de erros
    for col, dtype in columns_spec.items():
        if dtype.startswith('float'):
            # Substitui vírgulas por pontos e converte
            df[col] = df[col].astype(str).str.replace(',', '.')
            # Converte para numérico, forçando inválidos para NaN
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(dtype)
        else:
            df[col] = df[col].astype(dtype)
    
    # Pré-processa os dados para formato rápido de acesso
    cities_list = df['Município [-]'].unique().tolist()
    cities_data = {}
    
    for city in cities_list:
        city_data = df[df['Município [-]'] == city].iloc[0]
        cities_data[city] = {
            'basic': {
                'Código': city_data['Código [-]'],
                'Gentílico': city_data['Gentílico [-]'],
                'Prefeito': city_data['Prefeito [2025]']
            },
            'demographic': {
                'Área': city_data['Área Territorial - km² [2024]'],
                'População': city_data['População no último censo - pessoas [2022]'],
                'Densidade': city_data['Densidade demográfica - hab/km² [2022]'],
                'IDHM': city_data['IDHM (Índice de desenvolvimento humano municipal) [2010]']
            },
            'economic': {
                'PIB': city_data['PIB per capita - R$ [2021]'],
                'Receitas': city_data['Total de receitas brutas realizadas - R$ [2024]'],
                'Despesas': city_data['Total de despesas brutas empenhadas - R$ [2024]']
            }
        }
    
    return cities_list, cities_data

## 2. Carrega os dados uma única vez
CITIES_LIST, CITIES_DATA = load_data()

## 3. Função de formatação otimizada
def format_value(value):
    if pd.isna(value):
        return "N/D"
    if isinstance(value, (int, float)):
        if value >= 1000:
            return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{value:.2f}"
    return str(value)

## 4. Aplicativo Dash Otimizado
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

def home_page():
    return html.Div([
        html.H1("Selecione uma Cidade", style={'textAlign': 'center'}),
        html.Div(
            [html.Button(city, 
                        id={'type': 'city-btn', 'index': i},
                        style={'display': 'block', 'width': '100%', 'margin': '5px 0'})
             for i, city in enumerate(CITIES_LIST)],
            style={'height': '80vh', 'overflowY': 'auto', 'maxWidth': '600px', 'margin': '0 auto'}
        )
    ])

def city_page(city_name):
    data = CITIES_DATA.get(city_name)
    if not data:
        return html.Div([
            html.H1("Cidade não encontrada"),
            html.A("Voltar", href="/")
        ], style={'textAlign': 'center'})
    
    return html.Div([
        html.A("← Voltar", href="/", style={'margin': '20px'}),
        html.H1(city_name, style={'textAlign': 'center'}),
        
        html.Div([
            html.H2("Informações Básicas"),
            html.P(f"Código: {data['basic']['Código']}"),
            html.P(f"Gentílico: {data['basic']['Gentílico']}"),
            html.P(f"Prefeito: {data['basic']['Prefeito']}"),
            
            html.H2("Dados Demográficos"),
            html.P(f"Área: {format_value(data['demographic']['Área'])} km²"),
            html.P(f"População: {format_value(data['demographic']['População'])}"),
            html.P(f"Densidade: {format_value(data['demographic']['Densidade'])} hab/km²"),
            html.P(f"IDHM: {format_value(data['demographic']['IDHM'])}"),
            
            html.H2("Indicadores Econômicos"),
            html.P(f"PIB per capita: R$ {format_value(data['economic']['PIB'])}"),
            html.P(f"Receitas: R$ {format_value(data['economic']['Receitas'])}"),
            html.P(f"Despesas: R$ {format_value(data['economic']['Despesas'])}")
        ], style={'maxWidth': '800px', 'margin': '0 auto'})
    ])

@app.callback(
    Output('url', 'pathname'),
    Input({'type': 'city-btn', 'index': dash.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def navigate(clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    city_idx = eval(button_id)['index']
    return f'/{CITIES_LIST[city_idx]}'

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if not pathname or pathname == '/':
        return home_page()
    
    city_name = unquote(pathname[1:])
    return city_page(city_name)

if __name__ == '__main__':
    app.run(debug=True)