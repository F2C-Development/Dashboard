import dash
from dash import html, dcc, Input, Output, callback, State
import pandas as pd
from urllib.parse import unquote
import numpy as np

import dash_leaflet as dl
import json

import datetime
from data_export import cities_list, cities_dict


'''
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
'''

funds = pd.DataFrame([
    {"fund": "Fundo A", "min_dc": 10000000000, "max_rcl": 100000000000},
    {"fund": "Fundo B", "min_dc": 20000000000, "max_rcl": 100000000000},
    {"fund": "Fundo C", "min_dc": 5000000000, "max_rcl": 10000000000},
])

cidades = pd.read_csv('siconfi.txt')

CITIES_LIST, CITIES_DATA = cities_list, cities_dict

'''## 3. Função de formatação otimizada
def format_value(value):
    if pd.isna(value):
        return "N/D"
    if isinstance(value, (int, float)):
        if value >= 1000:
            return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{value:.2f}"
    return str(value)'''

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
    dados = CITIES_DATA.get(city_name)
    if not dados:
        return html.Div([
            html.H1("Cidade não encontrada"),
            html.A("Voltar", href="/")
        ], style={'textAlign': 'center'})

    # Dicionário que mapeia os 2 primeiros dígitos do código IBGE para a UF
    codigo_para_uf = {
        11: "RO", 12: "AC", 13: "AM", 14: "RR", 15: "PA", 16: "AP", 17: "TO",
        21: "MA", 22: "PI", 23: "CE", 24: "RN", 25: "PB", 26: "PE", 27: "AL", 28: "SE", 29: "BA",
        31: "MG", 32: "ES", 33: "RJ", 35: "SP",
        41: "PR", 42: "SC", 43: "RS",
        50: "MS", 51: "MT", 52: "GO", 53: "DF"
    }

    citycode = dados['basic']['Código']
    codigo_estado = int(str(citycode)[:2])
    uf = codigo_para_uf.get(codigo_estado, "Desconhecido")

    # Carrega o GeoJSON do estado
    with open(f'cityjsons/{uf}.json', 'r', encoding='utf-8') as f:
        estado_geojson = json.load(f)

    # Extrai a feature da cidade específica do GeoJSON do estado
    cidade_feature = None
    for feature in estado_geojson['features']:
        if feature['properties']['id'] == str(citycode):
            cidade_feature = {
                "type": "FeatureCollection",
                "features": [feature]
            }
            break

    # Configuração do centro do mapa (usando o primeiro ponto do polígono da cidade se disponível)
    center = dados.get('coordinates', [-15.7, -47.8])  # Fallback para Brasília
    if cidade_feature and cidade_feature['features'][0]['geometry']['coordinates']:
        # Pega o primeiro ponto do primeiro polígono (ajuste conforme seu GeoJSON)
        first_point = cidade_feature['features'][0]['geometry']['coordinates'][0][0]
        center = [first_point[1], first_point[0]]  # Inverte lat/long se necessário

    # Criação do mapa
    mapa = dl.Map(
        center=center,
        zoom=8,  # Zoom mais próximo para destacar a região
        children=[
            dl.TileLayer(),  # Adiciona mapa base
            dl.GeoJSON(
                id="estado-geojson",
                data=estado_geojson,
                style={
                    "weight": 1,
                    "color": "#4a4a4a",
                    "fillOpacity": 0.3,
                    "fillColor": "#6baed6"
                },
                hoverStyle={
                    "weight": 2,
                    "color": "#222",
                    "fillOpacity": 0.5
                }
            ),
            # Adiciona a cidade destacada se encontrada no GeoJSON do estado
            *([dl.GeoJSON(
                id="cidade-geojson",
                data=cidade_feature,
                style={
                    "weight": 2,
                    "color": "#d62728",
                    "fillOpacity": 0.7,
                    "fillColor": "#d62728"
                },
                zoomToBounds=True  # Ajusta o zoom para a cidade
            )] if cidade_feature else []),
            # Adiciona marcador como fallback se não encontrar a cidade no GeoJSON
            *([dl.Marker(
                position=center,
                children=[
                    dl.Tooltip(city_name),
                    dl.Popup(city_name)
                ]
            )] if not cidade_feature else [])
        ],
        style={
            'height': '60vh',
            'width': '100%',
            'margin': '20px 0',
            'borderRadius': '10px',
            'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'
        }
    )


    return html.Div([
        html.A("← Voltar", href="/", style={
            'margin': '20px',
            'display': 'inline-block',
            'textDecoration': 'none',
            'color': '#0074D9',
            'fontWeight': 'bold'
        }),
        
        html.Div([
            html.H1(city_name, style={'textAlign': 'center', 'marginBottom': '30px'}),
            
            # Layout principal com duas colunas
            html.Div([
                # Coluna esquerda - Informações
                html.Div([
                    # Seção de Informações Básicas
                    html.Div([
                        html.H2("Informações Básicas"),
                        html.P(f"Código IBGE: {citycode}"),
                        html.P(f"Gentílico: {dados['basic']['Gentílico']}"),
                        html.P(f"Prefeito: {dados['basic']['Prefeito']}"),
                    ], style={'marginBottom': '30px'}),
                    
                    # Seção de Dados Demográficos
                    html.Div([
                        html.H2("Dados Demográficos"),
                        html.P(f"Área: {dados['demographic']['Área']} km²"),
                        html.P(f"População: {dados['demographic']['População']}"),
                        html.P(f"Densidade: {dados['demographic']['Densidade']} hab/km²"),
                        html.P(f"IDHM: {dados['demographic']['IDHM']}"),
                    ], style={'marginBottom': '30px'}),
                    
                    # Seção de Indicadores Econômicos
                    html.Div([
                        html.H2("Indicadores Econômicos"),
                        html.P(f"PIB per capita: R$ {dados['economic']['PIB']}"),
                        html.P(f"Receitas: R$ {dados['economic']['Receitas']}"),
                        html.P(f"Despesas: R$ {dados['economic']['Despesas']}")
                    ])
                ], style={'flex': '1', 'padding': '0 20px'}),
                
                # Coluna direita - Mapa
                html.Div([
                    mapa
                ], style={'flex': '1', 'padding': '0 20px'})
            ], style={
                'display': 'flex',
                'gap': '30px',
                'maxWidth': '1400px',
                'margin': '0 auto'
            })
        ], style={
            'maxWidth': '1400px',
            'margin': '0 auto',
            'padding': '20px'
        }),
        html.Div(style={'fontFamily': 'Inter, sans-serif', "maxWidth": "600px", "margin": "left"}, children=[
            html.H2(id="city-info"),

            # Filter eligibility
            dcc.RadioItems(
                id="eligibility-filter",
                options=[
                    {"label": "Todos os fundos", "value": "all"},
                    {"label": "Apenas fundos elegíveis", "value": "eligible"},
                    {"label": "Apenas fundos não elegíveis", "value": "not_eligible"},
                ],
                value="all",
                inline=True,
                style={"marginTop": "10px"},
            ),

            html.Div(id="fund-list", style={"marginTop": "20px"}),
            ])
        ])

@app.callback(
    Output('url', 'pathname'),
    Input({'type': 'city-btn', 'index': dash.ALL}, 'n_clicks'),
    prevent_initial_call=True
    # Callback to update city info and funds eligibility
)
def navigate(clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return None
    
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

# Callback to update city info and funds eligibility
@app.callback(
    Output("city-info", "children"),
    Output("fund-list", "children"),
    Input("url", "pathname"),
    Input("eligibility-filter", "value"),
)
def update_dashboard(pathname, filter_eligibility):
    selected_city=unquote(pathname[1:])
    city = cidades[cidades["Município [-]"] == selected_city].iloc[0]

    # City info text
    city_text = f"Divída Consolidada: {city['DC [2024]']:,} | Renda Corrente Líquida: {city['RCL [2024]']:,}"

    # Determine eligibility for each fund
    def check_eligibility(row):
        pop_ok = city['DC [2024]'] >= row.min_dc
        gdp_ok = city['RCL [2024]'] <= row.max_rcl
        return pop_ok and gdp_ok

    funds["eligible"] = funds.apply(check_eligibility, axis=1)

    # Filter funds based on user choice
    if filter_eligibility == "eligible":
        filtered = funds[funds["eligible"]]
    elif filter_eligibility == "not_eligible":
        filtered = funds[~funds["eligible"]]
    else:
        filtered = funds

    # Build fund list elements
    fund_items = []
    for _, fund in filtered.iterrows():
        color = "green" if fund.eligible else "red"
        fund_items.append(html.Div([
            html.Strong(fund.fund, style={"color": color}),
            html.Span(f" (DC Min: {fund.min_dc:,}, RCL Max: {fund.max_rcl:,})",
                      style={"marginLeft": "8px", "color": "#555"}),
        ], style={"padding": "6px 0", "borderBottom": "1px solid #eee"}))

    if not fund_items:
        fund_items = [html.Em("Nenhum fundo corresponde ao filtro selecionado.")]

    return city_text, fund_items

if __name__ == '__main__':
    app.run(debug=True)