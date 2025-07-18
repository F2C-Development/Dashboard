import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
from urllib.parse import unquote
import json
import dash_leaflet as dl
from data_export import cities_dict,cities_list

## 1. Função de Carregamento de Dados (Original)
def load_data():
    df = pd.read_csv('ibge.txt')
    
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
    
    for col, dtype in columns_spec.items():
        if dtype.startswith('float'):
            df[col] = df[col].astype(str).str.replace(',', '.')
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(dtype)
        else:
            df[col] = df[col].astype(dtype)
    
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
                'População_Estimada': city_data['População estimada - pessoas [2024]'],
                'IDHM': city_data['IDHM (Índice de desenvolvimento humano municipal) [2010]']
            },
            'economic': {
                'PIB': city_data['PIB per capita - R$ [2021]'],
                'Receitas': city_data['Total de receitas brutas realizadas - R$ [2024]'],
                'Despesas': city_data['Total de despesas brutas empenhadas - R$ [2024]']
            }
        }
    
    return cities_list, cities_data

## 2. Carrega os dados
CITIES_LIST, CITIES_DATA = load_data()

## 3. Função de formatação (Original)
def format_value(value):
    if pd.isna(value):
        return "N/D"
    if isinstance(value, (int, float)):
        if value == int(value):
            value = int(value)
        if value >= 1000:
            return f"{value:,.0f}".replace(",", ".")
        return f"{value}"
    return str(value)

## 4. Aplicativo Dash com Estilo IBGE
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[
    {'href': 'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap', 'rel': 'stylesheet'}
])

server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    # Estilos globais
    html.Div(style={
        'fontFamily': '"Roboto", sans-serif',
        'color': '#333',
        'margin': '0',
        'minHeight': '100vh'
    })
])

def home_page():
    return html.Div([
        # Barra superior (mesmo estilo das páginas de cidade)
        html.Div([
            html.Span("Funds2", style={
                'color': 'white',
                'fontWeight': 'bold',
                'fontFamily': '"Roboto", sans-serif',
                'fontSize': '30px'
            }),
            html.Span("Cities", style={
                'color': 'white',
                'fontFamily': '"Roboto", sans-serif',
                'fontSize': '30px'
            }),
        ], style={
            'padding': '15px 30px',
            'borderBottom': '1px solid #ddd',
            'backgroundColor': 'rgb(7, 29, 75)',
            'marginBottom': '0',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center'
        }),
        
        # Container principal
        html.Div([
            # Coluna da lista de cidades (esquerda)
            html.Div([
                html.H1("Selecione uma Cidade", style={
                    'color': 'rgb(27, 119, 155)',
                    'fontSize': '28px',
                    'marginBottom': '20px',
                    'fontWeight': 'bold',
                    'fontFamily': '"Roboto", sans-serif',
                }),
                
                html.Div(
                    [html.Button(city, 
                                id={'type': 'city-btn', 'index': i},
                                style={
                                    'display': 'block',
                                    'width': '100%',
                                    'padding': '12px 15px',
                                    'margin': '8px 0',
                                    'border': '1px solid #ddd',
                                    'backgroundColor': '#fff',
                                    'color': '#333',
                                    'fontWeight': '400',
                                    'borderRadius': '4px',
                                    'cursor': 'pointer',
                                    'textAlign': 'left',
                                    'transition': 'all 0.3s',
                                    'fontFamily': '"Roboto", sans-serif',
                                    ':hover': {
                                        'backgroundColor': '#f0f7ff',
                                        'borderColor': '#1351B4',
                                        'transform': 'translateY(-2px)'
                                    }
                                })
                     for i, city in enumerate(CITIES_LIST)],
                    style={
                        'maxHeight': '70vh',
                        'overflowY': 'auto',
                        'paddingRight': '10px'
                    }
                )
            ], style={
                'flex': '1',
                'padding': '30px',
                'borderRight': '1px solid #ddd',
                'backgroundColor': 'rgb(230, 230, 230)',
                'marginRight': '30px'
            }),
            
            # Coluna de instruções (direita)
            html.Div([
                html.Div([
                    html.H2("Como usar", style={
                        'color': 'rgb(27, 119, 155)',
                        'borderBottom': '2px solid rgb(27, 119, 155)',
                        'paddingBottom': '5px',
                        'marginBottom': '20px',
                        'fontSize': '24px',
                        'fontWeight': 'bold',
                        'fontFamily': '"Roboto", sans-serif'
                    }),
                    
                    html.Div([
                        html.P("1. Selecione uma cidade na lista ao lado", style={
                            'color': '#555',
                            'marginBottom': '15px',
                            'fontSize': '18px',
                            'fontFamily': '"Roboto", sans-serif'
                        }),
                        
                        html.P("2. Visualize os dados completos do município", style={
                            'color': '#555',
                            'marginBottom': '15px',
                            'fontSize': '18px',
                            'fontFamily': '"Roboto", sans-serif'
                        }),
                        
                        html.P("3. Verifique os fundos disponíveis para a cidade", style={
                            'color': '#555',
                            'marginBottom': '15px',
                            'fontSize': '18px',
                            'fontFamily': '"Roboto", sans-serif'
                        }),
                        
                        html.P("4. Os ícones ✅ indicam verbas que a cidade se enquadra", style={
                            'color': '#555',
                            'marginBottom': '5px',
                            'fontSize': '18px',
                            'fontFamily': '"Roboto", sans-serif'
                        }),
                        
                        html.P("5. Os ícones ❌ indicam verbas não disponíveis", style={
                            'color': '#555',
                            'fontSize': '18px',
                            'fontFamily': '"Roboto", sans-serif'
                        })
                    ], style={
                        'padding': '20px',
                        'backgroundColor': '#fff',
                        'borderRadius': '8px',
                        'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
                    })
                ], style={
                    'marginBottom': '30px'
                }),
                
                html.Div([
                    html.H2("Critérios para Fundos", style={
                        'color': 'rgb(27, 119, 155)',
                        'borderBottom': '2px solid rgb(27, 119, 155)',
                        'paddingBottom': '5px',
                        'marginBottom': '20px',
                        'fontSize': '24px',
                        'fontWeight': 'bold',
                        'fontFamily': '"Roboto", sans-serif'
                    }),
                    
                    html.Div([
                        html.P("Verba Exemplo A:", style={
                            'color': '#333',
                            'fontWeight': '500',
                            'marginBottom': '5px',
                            'fontSize': '18px',
                            'fontFamily': '"Roboto", sans-serif'
                        }),
                        html.P("Receitas brutas > R$ 170.000", style={
                            'color': '#555',
                            'marginBottom': '15px',
                            'fontSize': '16px',
                            'fontFamily': '"Roboto", sans-serif'
                        }),
                        
                        html.P("Verba Exemplo B:", style={
                            'color': '#333',
                            'fontWeight': '500',
                            'marginBottom': '5px',
                            'fontSize': '18px',
                            'fontFamily': '"Roboto", sans-serif'
                        }),
                        html.P("Despesas brutas < R$ 150.000", style={
                            'color': '#555',
                            'fontSize': '16px',
                            'fontFamily': '"Roboto", sans-serif'
                        })
                    ], style={
                        'padding': '20px',
                        'backgroundColor': '#fff',
                        'borderRadius': '8px',
                        'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
                    })
                ])
            ], style={
                'flex': '1',
                'padding': '30px 30px 30px 0',
                'backgroundColor': 'rgb(230, 230, 230)'
            })
        ], style={
            'display': 'flex',
            'maxWidth': '1250px',
            'margin': '0 auto',
            'backgroundColor': 'rgb(230, 230, 230)',
            'minHeight': 'calc(100vh - 100px)'
        })
    ])

def city_page(city_name):
    dados = CITIES_DATA.get(city_name)
    if not dados:
        return html.Div([
            html.H1("Cidade não encontrada"),
            html.A("Voltar", href="/")
        ], style={'textAlign': 'center'})

    # === CÓDIGO DO MAPA (ORIGINAL) ===
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

    with open(f'cityjsons/{uf}.json', 'r', encoding='utf-8') as f:
        estado_geojson = json.load(f)

    cidade_feature = None
    for feature in estado_geojson['features']:
        if feature['properties']['id'] == str(citycode):
            cidade_feature = {
                "type": "FeatureCollection",
                "features": [feature]
            }
            break

    center = [-15.7, -47.8]  # Fallback
    if cidade_feature and cidade_feature['features'][0]['geometry']['coordinates']:
        first_point = cidade_feature['features'][0]['geometry']['coordinates'][0][0]
        center = [first_point[1], first_point[0]]

    mapa = dl.Map(
        center=center,
        zoom=8,
        children=[
            dl.TileLayer(),
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
            *([dl.GeoJSON(
                id="cidade-geojson",
                data=cidade_feature,
                style={
                    "weight": 2,
                    "color": "#d62728",
                    "fillOpacity": 0.7,
                    "fillColor": "#d62728"
                },
                zoomToBounds=True
            )] if cidade_feature else []),
            *([dl.Marker(
                position=center,
                children=[
                    dl.Tooltip(city_name),
                    dl.Popup(city_name)
                ]
            )] if not cidade_feature else [])
        ],
        style={
            'height': '70vh',  # Aumentado de 60vh para 70vh
            'width': '100%',
            'borderRadius': '8px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        }
    )
    # === FIM DO CÓDIGO DO MAPA ===

    return html.Div([
        # Barra superior
        html.Div([
            html.A("Voltar", href="/", style={
                'color': 'white',
                'fontWeight': 'bold',
                'textDecoration': 'none',
                'marginRight': '20px',
                'position': 'absolute',  # Posiciona absolutamente
                'left': '20px',
                'fontFamily': '"Roboto", sans-serif',
            }),
            html.Span("Funds2", style={
                'color': 'white',
                'fontWeight': 'bold',
                'fontFamily': '"Roboto", sans-serif',
                'fontSize': '30px'
            }),
            html.Span("Cities", style={
                'color': 'white',
                'fontFamily': '"Roboto", sans-serif',
                'fontSize': '30px'
            }),
        ], style={
            'padding': '15px 30px',
            'borderBottom': '1px solid #ddd',
            'backgroundColor': 'rgb(7, 29, 75)',
            'marginBottom': '0',
            'position': 'relative',  # Container relativo para posicionamento absoluto interno
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center'  # Centraliza horizontalmente
        }),
        
        # Container principal
        html.Div([
            # Coluna de informações (esquerda)
            html.Div([
                html.H1(city_name, style={
                    'color': 'rgb(27, 119, 155)',
                    'fontSize': '28px',
                    'marginBottom': '10px',
                    'fontWeight': 'bold',
                    'fontFamily': '"Roboto", sans-serif',
                }),
                
                html.Div([
                    html.Span(f"Código do Município: {citycode}", style={
                        'color': '#555',
                        'marginRight': '20px',
                        'fontWeight': '300',
                        'fontFamily': '"Roboto", sans-serif',
                    }),
                    html.Span(f"Gentílico: {dados['basic']['Gentílico'].lower()}", style={
                        'color': '#555',
                        'marginRight': '20px',
                        'fontWeight': '300',
                        'fontFamily': '"Roboto", sans-serif',
                    }),
                    html.Span(f"Estado: {uf}", style={
                        'color': '#555',
                        'fontWeight': '300',
                        'fontFamily': '"Roboto", sans-serif',
                    }),
                ], style={'marginBottom': '15px'}),
                
                html.Div([
                    html.Span(f"Prefeito: {dados['basic']['Prefeito'].title()}", style={
                        'color': '#333',
                        'fontFamily': '"Roboto", sans-serif',
                    })
                ], style={'marginBottom': '30px'}),

                # Seção FUNDOS
                html.Div([
                    html.H2("FUNDOS", style={
                        'color': 'rgb(27, 119, 155)',
                        'borderBottom': '2px solid rgb(27, 119, 155)',
                        'paddingBottom': '5px',
                        'marginBottom': '20px',
                        'fontSize': '20px',
                        'fontWeight': 'bold',
                        'fontFamily': '"Roboto", sans-serif'
                    }),
                    
                    html.Div([
                        # Verba Exemplo A
                        html.Div([
                            html.P("Verba Exemplo A:", style={
                                'color': '#555',
                                'marginBottom': '5px',
                                'fontWeight': '300',
                                'fontFamily': '"Roboto", sans-serif',
                                'fontSize': '20px',
                                'display': 'inline-block',
                                'marginRight': '10px'
                            }),
                            html.Span(
                                "✅" if dados['economic']['Receitas'] > 170000 else "❌",
                                style={
                                    'color': 'green' if dados['economic']['Receitas'] > 170000 else 'red',
                                    'fontSize': '20px'
                                }
                            ),
                            html.P("(Receita > R$ 170.000)", style={
                                'color': '#555',
                                'fontWeight': '300',
                                'fontFamily': '"Roboto", sans-serif',
                                'fontSize': '16px',
                                'marginTop': '5px'
                            })
                        ], style={'marginBottom': '15px'}),
                        
                        # Verba Exemplo B
                        html.Div([
                            html.P("Verba Exemplo B:", style={
                                'color': '#555',
                                'marginBottom': '5px',
                                'fontWeight': '300',
                                'fontFamily': '"Roboto", sans-serif',
                                'fontSize': '20px',
                                'display': 'inline-block',
                                'marginRight': '10px'
                            }),
                            html.Span(
                                "✅" if dados['economic']['Despesas'] < 150000 else "❌",
                                style={
                                    'color': 'green' if dados['economic']['Despesas'] < 150000 else 'red',
                                    'fontSize': '20px'
                                }
                            ),
                            html.P("(Despesas < R$ 150.000)", style={
                                'color': '#555',
                                'fontWeight': '300',
                                'fontFamily': '"Roboto", sans-serif',
                                'fontSize': '16px',
                                'marginTop': '5px'
                            })
                        ])
                    ])
                ], style={
                    'backgroundColor': '#fff',
                    'padding': '20px',
                    'borderRadius': '8px',
                    'marginBottom': '30px',
                    'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
                }),
                
                # Seção POPULAÇÃO
                html.Div([
                    html.H2("POPULAÇÃO", style={
                        'color': 'rgb(27, 119, 155)',
                        'borderBottom': '2px solid rgb(27, 119, 155)',
                        'paddingBottom': '5px',
                        'marginBottom': '20px',
                        'fontSize': '20px',
                        'fontWeight': 'bold',
                        'fontFamily': '"Roboto", sans-serif',
                    }),
                    
                    html.Div([
                        html.P("População no último censo [2022]:", style={
                            'color': '#555',
                            'marginBottom': '5px',
                            'fontWeight': '300',
                            'fontFamily': '"Roboto", sans-serif',
                            'fontSize': '20px'
                        }),
                        html.P(f"{format_value(dados['demographic']['População'])} pessoas", style={
                            'fontWeight': '400',
                            'fontSize': '18px',
                            'color': '#333',
                            'marginBottom': '20px',
                            'fontFamily': '"Roboto", sans-serif',
                        }),
                        
                        html.P("População estimada [2024]:", style={
                            'color': '#555',
                            'marginBottom': '5px',
                            'fontWeight': '300',
                            'fontFamily': '"Roboto", sans-serif',
                            'fontSize': '20px'
                        }),
                        html.P(f"{format_value(dados['demographic']['População_Estimada'])} pessoas", style={
                            'fontWeight': '400',
                            'fontSize': '18px',
                            'color': '#333',
                            'marginBottom': '20px',
                            'fontFamily': '"Roboto", sans-serif'
                        }),
                        
                        html.P("Densidade demográfica [2022]:", style={
                            'color': '#555',
                            'marginBottom': '5px',
                            'fontWeight': '300',
                            'fontFamily': '"Roboto", sans-serif',
                            'fontSize': '20px'
                        }),
                        html.P(f"{format_value(dados['demographic']['Densidade'])} hab/km²", style={
                            'fontWeight': '400',
                            'fontSize': '18px',
                            'color': '#333',
                            'fontFamily': '"Roboto", sans-serif'
                        })
                    ])
                ], style={
                    'backgroundColor': '#fff',
                    'padding': '20px',
                    'borderRadius': '8px',
                    'marginBottom': '30px',
                    'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
                }),
                
                # Seção TRABALHO E RENDIMENTO
                html.Div([
                    html.H2("TRABALHO E RENDIMENTO", style={
                        'color': 'rgb(27, 119, 155)',
                        'borderBottom': '2px solid rgb(27, 119, 155)',
                        'paddingBottom': '5px',
                        'marginBottom': '20px',
                        'fontSize': '20px',
                        'fontWeight': 'bold',
                        'fontFamily': '"Roboto", sans-serif'
                    }),
                    
                    html.Div([
                        html.P("PIB per capita [2021]:", style={
                            'color': '#555',
                            'marginBottom': '5px',
                            'fontWeight': '300',
                            'fontFamily': '"Roboto", sans-serif',
                            'fontSize': '20px'
                        }),
                        html.P(f"R$ {format_value(dados['economic']['PIB'])}", style={
                            'fontWeight': '400',
                            'fontSize': '18px',
                            'color': '#333',
                            'fontFamily': '"Roboto", sans-serif'
                        }),
                        
                        html.P("Receitas [2024]:", style={
                            'color': '#555',
                            'marginBottom': '5px',
                            'fontWeight': '300',
                            'fontFamily': '"Roboto", sans-serif',
                            'fontSize': '20px'
                        }),
                        html.P(f"R$ {format_value(dados['economic']['Receitas'])}", style={
                            'fontWeight': '400',
                            'fontSize': '18px',
                            'color': '#333',
                            'fontFamily': '"Roboto", sans-serif'
                        }),
                        
                        html.P("Despesas [2024]:", style={
                            'color': '#555',
                            'marginBottom': '5px',
                            'fontWeight': '300',
                            'fontFamily': '"Roboto", sans-serif',
                            'fontSize': '20px'
                        }),
                        html.P(f"R$ {format_value(dados['economic']['Despesas'])}", style={
                            'fontWeight': '400',
                            'fontSize': '18px',
                            'color': '#333',
                            'fontFamily': '"Roboto", sans-serif'
                        })
                    ])
                ], style={
                    'backgroundColor': '#fff',
                    'padding': '20px',
                    'borderRadius': '8px',
                    'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
                })
            ], style={
                'flex': '1',
                'padding': '20px 30px 20px 20px',  # Mais padding à esquerda
                'borderRight': '1px solid #ddd',
                'backgroundColor': 'rgb(230, 230, 230)',
                'marginRight': '30px'
            }),
            
            # Coluna do mapa (direita)
            html.Div([
                mapa
            ], style={
                'flex': '1',
                'padding': '20px 30px 20px 0',  # Ajuste de padding
                'minWidth': '0'  # Permite que o mapa ocupe mais espaço
            })
        ], style={
            'display': 'flex',
            'maxWidth': '1250px',
            'margin': '0 auto 30px auto',  # Adicionado margin-bottom de 30px
            'backgroundColor': 'rgb(230, 230, 230)',
            'minHeight': 'calc(100vh - 100px)',  # Ajuste conforme necessário
            'overflow': 'hidden'  # Opcional: evita vazamento do conteúdo
        })
    ], style={
        'paddingBottom': '0px'  # Remove padding extra
    })

@app.callback(
    Output('url', 'pathname'),
    Input({'type': 'city-btn', 'index': dash.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def navigate(clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
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