import dash
from dash import html, dcc, Input, Output, callback, State
import dash_leaflet as dl
import pandas as pd
import json

app = dash.Dash(__name__, external_stylesheets=[
    {'href': 'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap', 'rel': 'stylesheet'}
])
server = app.server

# 1. Carregar dados financeiros
dados = pd.read_csv("siconfi.txt")

# 2. Carregar GeoJSON
with open('br_states.json', 'r', encoding='utf-8') as f:
    estados_geojson = json.load(f)

# 3. Configuração do Mapa
mapa = dl.Map(
    center=[-14.2350, -51.9253],
    zoom=4,
    children=[
        dl.TileLayer(),
        dl.GeoJSON(
            id="estados-geojson",
            data=estados_geojson,
            format="geojson",
            zoomToBoundsOnClick=True,
            hoverStyle=dict(weight=3, color='#666', fillOpacity=0.7),
            style=dict(weight=1, color='#4a4a4a', fillOpacity=0.3, fillColor='#6baed6')
        )
    ],
    style={
        'height': '70vh',
        'width': '100%',
        'borderRadius': '8px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
    }
)

# 4. Layout do App
app.layout = html.Div([
    # Barra superior
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
        })
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
        # Coluna de informações (esquerda)
        html.Div([
            html.H2("MUNICÍPIOS - VERBA EXEMPLO A", style={
                'color': 'rgb(27, 119, 155)',
                'borderBottom': '2px solid rgb(27, 119, 155)',
                'paddingBottom': '5px',
                'marginBottom': '20px',
                'fontSize': '20px',
                'fontWeight': 'bold',
                'fontFamily': '"Roboto", sans-serif'
            }),
            
            html.Div(id="info-estado", style={
                'backgroundColor': '#fff',
                'padding': '20px',
                'borderRadius': '8px',
                'marginBottom': '20px',
                'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
            }),
            
            html.Div([
                html.Div(
                    id="lista-municipios",
                    style={
                        'overflowY': 'auto',
                        'height': '60vh',
                        'paddingRight': '10px'
                    }
                )
            ], style={
                'backgroundColor': '#fff',
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
            })
        ], style={
            'flex': '1',
            'padding': '20px 30px 20px 20px',
            'borderRight': '1px solid #ddd',
            'backgroundColor': 'rgb(230, 230, 230)',
            'marginRight': '30px'
        }),
        
        # Coluna do mapa (direita)
        html.Div([
            html.H2("SELECIONE UM ESTADO", style={
                'color': 'rgb(27, 119, 155)',
                'borderBottom': '2px solid rgb(27, 119, 155)',
                'paddingBottom': '5px',
                'marginBottom': '15px',
                'fontSize': '20px',
                'fontWeight': 'bold',
                'fontFamily': '"Roboto", sans-serif'
            }),
            html.P("Clique em um estado no mapa para ver os municípios elegíveis para a Verba Exemplo A", style={
                'color': '#555',
                'fontFamily': '"Roboto", sans-serif',
                'marginBottom': '15px'
            }),
            mapa
        ], style={
            'flex': '1',
            'padding': '20px 30px 20px 0',
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

# 5. Callback para interatividade
@app.callback(
    [Output("info-estado", "children"),
     Output("lista-municipios", "children"),
     Output("estados-geojson", "hideout")],
    [Input("estados-geojson", "clickData")],
    prevent_initial_call=True
)
def update_info(click_data):
    if not click_data:
        return (
            html.Div("Selecione um estado no mapa para ver os municípios", style={
                'color': '#555',
                'fontFamily': '"Roboto", sans-serif'
            }),
            "",
            dash.no_update
        )
    
    try:
        # Obtém a sigla do estado clicado
        sigla = click_data['id']
        nome_estado = click_data['properties']['name'] if 'properties' in click_data and 'name' in click_data['properties'] else sigla
        
        # Filtra municípios do estado
        municipios = dados[dados['UF [-]'] == sigla].copy()
        
        # Verifica elegibilidade
        municipios['Elegivel'] = municipios['RCL [2024]'].apply(
            lambda x: float(x) >= 100000000 if pd.notnull(x) and str(x).replace('.','').isdigit() else False
        )
        
        # Ordena por elegibilidade (elegíveis primeiro) e depois por nome
        municipios = municipios.sort_values(['Elegivel', 'Município [-]'], ascending=[False, True])
        
        # Cria info do estado
        info_estado = html.Div([
            html.H3(f"{nome_estado} ({sigla})", style={
                'color': 'rgb(27, 119, 155)',
                'fontFamily': '"Roboto", sans-serif',
                'marginBottom': '10px'
            }),
            html.P(f"Total de municípios: {len(municipios)}", style={
                'color': '#555',
                'fontFamily': '"Roboto", sans-serif'
            }),
            html.P(f"Municípios elegíveis: {sum(municipios['Elegivel'])}", style={
                'color': 'green',
                'fontFamily': '"Roboto", sans-serif',
                'fontWeight': 'bold'
            })
        ])
        
        # Cria lista de municípios organizada
        municipios_elegiveis = []
        municipios_nao_elegiveis = []
        
        for _, row in municipios.iterrows():
            item = html.Div([
                html.P(html.Strong(row['Município [-]']), style={
                    'fontFamily': '"Roboto", sans-serif',
                    'marginBottom': '5px'
                }),
                html.P(f"RCL: R${float(row['RCL [2024]']):,.2f}" if pd.notnull(row['RCL [2024]']) else "RCL: N/D", 
                      style={'color': '#555', 'fontFamily': '"Roboto", sans-serif'}),
                html.P(
                    "✅ Elegível" if row['Elegivel'] else "❌ Não elegível",
                    style={
                        'color': 'green' if row['Elegivel'] else 'red',
                        'fontWeight': 'bold',
                        'fontFamily': '"Roboto", sans-serif'
                    }
                ),
                html.Hr(style={'margin': '15px 0', 'borderColor': '#eee'})
            ], style={
                'padding': '15px',
                'backgroundColor': '#f8f8f8',
                'borderLeft': '4px solid green' if row['Elegivel'] else '4px solid red',
                'marginBottom': '10px'
            })
            
            if row['Elegivel']:
                municipios_elegiveis.append(item)
            else:
                municipios_nao_elegiveis.append(item)
        
        # Monta a lista final com seções
        lista_final = []
        
        if municipios_elegiveis:
            lista_final.append(html.H4("Municípios Elegíveis", style={
                'color': 'green',
                'fontFamily': '"Roboto", sans-serif',
                'marginTop': '10px'
            }))
            lista_final.extend(municipios_elegiveis)
        
        if municipios_nao_elegiveis:
            lista_final.append(html.H4("Municípios Não Elegíveis", style={
                'color': 'red',
                'fontFamily': '"Roboto", sans-serif',
                'marginTop': '20px' if municipios_elegiveis else '10px'
            }))
            lista_final.extend(municipios_nao_elegiveis)
        
        # Prepara o estilo do mapa
        new_hideout = {
            "clickedFeature": sigla,
            "style": {
                "clicked": {
                    "weight": 2,
                    "color": "#d62728",
                    "fillOpacity": 0.7
                }
            }
        }
        
        return info_estado, html.Div(lista_final), new_hideout
    
    except Exception as e:
        print(f"Erro: {str(e)}")
        return (
            html.Div("Ocorreu um erro ao carregar os dados", style={
                'color': 'red',
                'fontFamily': '"Roboto", sans-serif'
            }),
            "",
            dash.no_update
        )

if __name__ == '__main__':
    app.run(debug=True)