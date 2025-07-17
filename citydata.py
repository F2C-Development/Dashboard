import pandas as pd

## 3. Função de formatação otimizada
def format_value(value):
    if pd.isna(value):
        return "N/D"
    if isinstance(value, (int, float)):
        if value >= 1000:
            return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{value:.2f}"
    return str(value)

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
                'Área': format_value(city_data['Área Territorial - km² [2024]']),
                'População': format_value(city_data['População no último censo - pessoas [2022]']),
                'Densidade': format_value(city_data['Densidade demográfica - hab/km² [2022]']),
                'IDHM': format_value(city_data['IDHM (Índice de desenvolvimento humano municipal) [2010]'])
            },
            'economic': {
                'PIB': format_value(city_data['PIB per capita - R$ [2021]']),
                'Receitas': format_value(city_data['Total de receitas brutas realizadas - R$ [2024]']),
                'Despesas': format_value(city_data['Total de despesas brutas empenhadas - R$ [2024]'])
            }
        }
    
    return cities_list, cities_data

cities_list,cities_dict=load_data()

# Save to a new .py file
with open('data_export.py', 'w') as f:
    f.write("import numpy as np \n")
    f.write("from numpy import nan \n")
    f.write(f"cities_list = {repr(cities_list)}\n")
    f.write(f"cities_dict = {repr(cities_dict)}\n")




