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

# 3. Configuração do Mapa - Centralização ajustada para o Brasil
mapa = dl.Map(
    center=[-14.2350, -51.9253],  # Coordenadas centralizadas no Brasil
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
        
        # Coluna do mapa (direita) - Sem container branco
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
            mapa  # Mapa diretamente no fundo cinza, sem container branco
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
    [State("estados-geojson", "hideout")],
    prevent_initial_call=True
)
def update_info(click_data, current_hideout):
    if not click_data:
        return html.Div([
            html.H2("Selecione um estado", style={
                'color': 'rgb(27, 119, 155)',
                'fontFamily': '"Roboto", sans-serif'
            }),
            html.P("Clique em um estado no mapa para ver os municípios elegíveis para a Verba Exemplo A", style={
                'color': '#555',
                'fontFamily': '"Roboto", sans-serif'
            })
        ]), "", dash.no_update
    
    try:
        # Obtém a sigla do estado clicado
        sigla = click_data['id']
        nome_estado = click_data['geometry_name']
        
        # Filtra municípios do estado
        municipios = dados[dados['UF [-]'] == sigla].sort_values('Município [-]')
        
        if municipios.empty:
            return html.Div([
                html.H2(f"{nome_estado} ({sigla})", style={
                    'color': 'rgb(27, 119, 155)',
                    'fontFamily': '"Roboto", sans-serif'
                }),
                html.Hr(style={'borderColor': '#eee'}),
                html.P("Nenhum município encontrado para este estado.", style={
                    'color': '#555',
                    'fontFamily': '"Roboto", sans-serif'
                })
            ]), "", dash.no_update
        
        # Info do estado
        info_estado = html.Div([
            html.H2(f"{nome_estado} ({sigla})", style={
                'color': 'rgb(27, 119, 155)',
                'fontFamily': '"Roboto", sans-serif'
            }),
            html.Hr(style={'borderColor': '#eee'}),
            html.P(f"Total de municípios: {len(municipios)}", style={
                'color': '#555',
                'fontFamily': '"Roboto", sans-serif',
                'fontSize': '16px'
            }),
            html.P("Critério para Verba Exemplo A: RCL ≥ R$ 100.000.000,00", style={
                'color': '#555',
                'fontFamily': '"Roboto", sans-serif',
                'fontSize': '14px',
                'fontWeight': 'bold',
                'marginTop': '10px'
            })
        ])
        
        # Lista de todos os municípios com informação de elegibilidade
        lista_itens = []
        for _, row in municipios.iterrows():
            elegivel = False
            if 'RCL [-]' in row:
                try:
                    elegivel = float(row['RCL [-]']) >= 100000000
                except:
                    elegivel = False
            
            item = html.Div([
                html.P([
                    html.Strong(row['Município [-]'], style={
                        'fontFamily': '"Roboto", sans-serif',
                        'fontSize': '16px',
                        'color': '#333',
                        'marginBottom': '5px'
                    })
                ]),
                html.P([
                    (f"RCL: R${float(row['RCL [-]']):,.2f}" if 'RCL [-]' in row else "RCL: N/D")
                ], style={
                    'color': '#555',
                    'fontFamily': '"Roboto", sans-serif',
                    'fontSize': '14px',
                    'marginBottom': '5px'
                }),
                html.P(
                    "✅ Elegível para Verba Exemplo A" if elegivel else "❌ Não elegível para Verba Exemplo A",
                    style={
                        'fontFamily': '"Roboto", sans-serif',
                        'color': 'green' if elegivel else 'red',
                        'fontWeight': 'bold',
                        'fontSize': '14px',
                        'marginBottom': '0'
                    }
                ),
                html.Hr(style={
                    'margin': '15px 0',
                    'borderColor': '#eee',
                    'borderWidth': '1px'
                })
            ], style={
                'padding': '15px',
                'backgroundColor': '#f9f9f9',
                'borderRadius': '5px',
                'marginBottom': '10px'
            })
            
            lista_itens.append(item)
        
        lista = html.Div(lista_itens)
        
        # Prepara o novo estilo para destacar apenas o estado selecionado
        new_hideout = {
            "clickedFeature": sigla,
            "style": {
                "clicked": {
                    "weight": 2,
                    "color": "#d62728",
                    "fillOpacity": 0.7,
                    "fillColor": "#d62728"
                }
            }
        }
        
        return info_estado, lista, new_hideout
    
    except Exception as e:
        print(f"Erro: {str(e)}")
        return html.Div([
            html.H2("Erro", style={
                'color': 'rgb(27, 119, 155)',
                'fontFamily': '"Roboto", sans-serif'
            }),
            html.Hr(style={'borderColor': '#eee'}),
            html.P(f"Ocorreu um erro ao processar os dados: {str(e)}", style={
                'color': '#555',
                'fontFamily': '"Roboto", sans-serif'
            })
        ]), "", dash.no_update

if __name__ == '__main__':
    app.run(debug=True)