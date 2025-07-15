import dash
from dash import html, dcc, Input, Output
import pandas as pd

# Example mock data
cidades=pd.read_csv('siconfi.txt')

funds = pd.DataFrame([
    {"fund": "Fundo A", "min_dc": 10000000000, "max_rcl": 100000000000},
    {"fund": "Fundo B", "min_dc": 20000000000, "max_rcl": 100000000000},
    {"fund": "Fundo C", "min_dc": 5000000000, "max_rcl": 10000000000},
])

# Initialize app
app = dash.Dash(__name__)

app.layout = html.Div(style={"fontFamily": "Arial, sans-serif", "maxWidth": "600px", "margin": "auto"}, children=[
    html.H1("Funds2Cities"),

    # City selector
    dcc.Dropdown(
        id="city-dropdown",
        options=[{"label": c, "value": c} for c in cidades["Município [-]"]],
        value="São Paulo",
        clearable=False,
    ),

    html.H3(id="city-info"),

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

# Callback to update city info and funds eligibility
@app.callback(
    Output("city-info", "children"),
    Output("fund-list", "children"),
    Input("city-dropdown", "value"),
    Input("eligibility-filter", "value"),
)
def update_dashboard(selected_city, filter_eligibility):
    city = cidades[cidades["Município [-]"] == selected_city].iloc[0]

    # City info text
    city_text = f"Divída Consolidada: {city.DC:,} | Renda Corrente Líquida: {city.RCL:,}"

    # Determine eligibility for each fund
    def check_eligibility(row):
        pop_ok = city.DC >= row.min_dc
        gdp_ok = city.RCL <= row.max_rcl
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

if __name__ == "__main__":
    app.run(debug=True)
