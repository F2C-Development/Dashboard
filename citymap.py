import dash
from dash import html, dcc, Input, Output, callback, State
import dash_leaflet as dl
import pandas as pd
import json

app = dash.Dash(__name__)
server = app.server

# 1. Carregar dados financeiros
dados = pd.read_csv("sincofi.txt")

# 2. Carregar GeoJSON
with open('br_states.json', 'r', encoding='utf-8') as f:
    estados_geojson = json.load(f)

# 3. Configuração do Mapa
mapa = dl.Map(
    center=[-15.7, -47.8],
    zoom=4,
    children=[
        #dl.TileLayer(),
        dl.GeoJSON(
            id="estados-geojson",
            data=estados_geojson,
            format="geojson",
            zoomToBoundsOnClick=True,
            hoverStyle={
                "weight": 3,
                "color": "#666",
                "fillOpacity": 0.7
            },
            style={
                "weight": 2,
                "color": "#444",
                "fillOpacity": 0.5,
                "fillColor": "#6baed6"
            }
        )
    ],
    style={'height': '80vh', 'width': '100%', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'background': 'lightgrey'}
)

# 4. Layout do App
app.layout = html.Div([
    html.H1("Funds2Cities - Verba Exemplo", style={'fontFamily': 'Inter, sans-serif', 'textAlign': 'center', 'marginBottom': '30px'}),
    
    html.Div([
        # Coluna da esquerda - Lista de municípios
        html.Div([
            html.Div(id="info-estado", style={
                'padding': '20px',
                'backgroundColor': '#f8f9fa',
                'borderRadius': '10px',
                'marginBottom': '20px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'height': 'fit-content'
            }),
            html.Div(
                id="lista-municipios-container",
                style={
                    'height': 'calc(65vh - 20px)',  # Subtrai a margem inferior do info-estado
                    'border': '1px solid #ddd',
                    'borderRadius': '10px',
                    'backgroundColor': '#f8f9fa',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflow': 'hidden'  # Garante que nada ultrapasse este container
                },
                children=[
                    html.Div(
                        id="lista-municipios",
                        style={
                            'overflowY': 'auto',
                            'padding': '15px',
                            'height': '100%',  # Ocupa todo o espaço disponível
                            'boxSizing': 'border-box'  # Inclui padding na altura total
                        }
                    )
                ]
            )
        ], style={
            'width': '38%',
            'display': 'inline-block',
            'verticalAlign': 'top',
            'padding': '0 15px',
            'height': '80vh',  # Altura fixa para a coluna esquerda
            'overflow': 'hidden'  # Garante que nada ultrapasse
        }),
        
        # Coluna da direita - Mapa
        html.Div(mapa, style={
            'width': '60%',
            'display': 'inline-block',
            'verticalAlign': 'top',
            'padding': '0 15px',
            'height': '80vh'  # Altura fixa para a coluna direita
        })
    ], style={
        'display': 'flex',
        'justifyContent': 'space-between',
        'padding': '0 20px',
        'height': '80vh',  # Altura fixa para o container principal
        'overflow': 'hidden'  # Garante que nada ultrapasse
    })
])

# 5. Callback para interatividade
@app.callback(
    [Output("info-estado", "children"),
     Output("lista-municipios", "children"),
     Output("estados-geojson", "style")],
    [Input("estados-geojson", "clickData")],
    prevent_initial_call=True
)
def update_info(click_data):
    if not click_data:
        return "Clique em um estado para ver detalhes", "", dash.no_update
    
    try:
        # Obtém a sigla do estado clicado
        sigla = click_data['id']
        nome_estado = click_data['geometry_name']
        
        # Filtra municípios do estado
        municipios = dados[dados['UF'] == sigla].sort_values('Nome')
        
        if municipios.empty:
            return html.Div([
                html.H2(f"{nome_estado} ({sigla})", style={'fontFamily': 'Inter, sans-serif'}),
                html.Hr(),
                html.P("Nenhum município encontrado para este estado.")
            ]), "", dash.no_update
        
        # Info do estado
        info_estado = html.Div([
            html.H2(f"{nome_estado} ({sigla})", style={'fontFamily': 'Inter, sans-serif', 'color': '#2c3e50'}),
            html.Hr(),
            html.P(f"Total de municípios: {len(municipios)}", style={'fontFamily': 'Inter, sans-serif', 'fontSize': '16px'})
        ])
        
        # Lista de todos os municípios com informação de elegibilidade
        lista_itens = []
        for _, row in municipios.iterrows():
            elegivel = False
            if 'RCL' in row:
                try:
                    elegivel = float(row['RCL']) >= 100000000000
                except:
                    elegivel = False
            
            item = html.Li([
                html.Strong(row['Nome'], style={'fontFamily': 'Inter, sans-serif', 'fontSize': '15px'}),
                html.Br(),
                (f"DC: R${float(row['DC']):,.2f} | " if 'DC' in row else ""),
                (f"RCL: R${float(row['RCL']):,.2f}" if 'RCL' in row else ""),
                html.Br(),
                html.Span(
                    "✅ Elegível" if elegivel else "❌ Não elegível",
                    style={
                        'fontFamily': 'Inter, sans-serif',
                        'color': 'green' if elegivel else 'red',
                        'fontWeight': 'bold',
                        'fontSize': '14px'
                    }
                ),
                html.Hr(style={'margin': '10px 0'})
            ], style={
                'marginBottom': '10px', 
                'padding': '8px', 
                'backgroundColor': 'white', 
                'borderRadius': '5px',
                'overflow': 'hidden'
            })
            
            lista_itens.append(item)
        
        lista = html.Ul(lista_itens, style={
            'listStyleType': 'none',
            'paddingLeft': '0',
            'marginTop': '0',
            'marginBottom': '0'
        })
        
        # Prepara o novo estilo para destacar o estado selecionado
        new_style = {
            "default": {
                "weight": 2,
                "color": "#444",
                "fillOpacity": 0.5,
                "fillColor": "#6baed6"
            },
            "clicked": {
                "weight": 3,
                "color": "#222",
                "fillOpacity": 0.7,
                "fillColor": "#4CAF50"  # Verde para o estado selecionado
            },
            "clickedFeature": sigla
        }
        
        return info_estado, lista, new_style
    
    except Exception as e:
        print(f"Erro: {str(e)}")
        return html.Div([
            html.H2("Erro"),
            html.Hr(),
            html.P(f"Ocorreu um erro ao processar os dados: {str(e)}")
        ]), "", dash.no_update

if __name__ == '__main__':
    app.run(debug=True)