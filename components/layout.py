from dash import dcc, html

graph_types = [
    # Базовые (используются в 80% случаев)
    {'label': 'Столбчатая', 'value': 'bar'},
    {'label': 'Линейный', 'value': 'line'},
    {'label': 'Круговая', 'value': 'pie'},
    {'label': 'Точечная', 'value': 'scatter'},

    # Статистические
    {'label': 'Гистограмма', 'value': 'histogram'},
    {'label': 'Ящик с усами', 'value': 'box'},

    # Специальные
    {'label': 'Тепловая карта', 'value': 'heatmap'},
    {'label': 'Биржевая (свечная)', 'value': 'candlestick'},
    {'label': 'Пузырьковая', 'value': 'bubble'},

    # Расширенные
    {'label': 'Диаграмма Санкея', 'value': 'sankey'},
    {'label': 'Географическая карта', 'value': 'choropleth'},
    {'label': 'График Ганта', 'value': 'gantt'},

    # Для корпоративных клиентов
    {'label': 'Комбинированная', 'value': 'combo'},
]


def create_layout():
    return html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Button('Загрузить CSV/Excel', style={
                'padding': '10px 20px',
                'border': 'none',
                'background': '#4CAF50',
                'color': 'white',
                'cursor': 'pointer'
            }),
            multiple=False,
            style={'margin': '20px'}
        ),

        html.Div(id='output-data-upload'),

        dcc.Dropdown(
            id='graph-type',
            options=graph_types,
            value='scatter',
            placeholder="Выберите тип графика",
            style={'width': '100%', 'margin': '10px 0'}
        ),

        dcc.Dropdown(
            id='x-axis',
            placeholder="Ось X",
            style={'width': '100%', 'margin': '10px 0'}
        ),

        dcc.Dropdown(
            id='y-axis',
            placeholder="Ось Y",
            style={'width': '100%', 'margin': '10px 0'}
        ),

        dcc.Dropdown(
            id='z-axis',
            placeholder="Ось Z (для 3D)",
            style={'width': '100%', 'margin': '10px 0'}
        ),

        dcc.Graph(
            id='graph',
            style={'height': '70vh', 'margin': '20px 0'}
        ),

        html.Div(id='notification', style={
            'position': 'fixed',
            'top': '20px',
            'right': '20px',
            'width': '300px',
            'padding': '15px',
            'background-color': '#ffdddd',
            'border': '1px solid #ff9999',
            'border-radius': '5px',
            'display': 'none',
            'z-index': '1000'
        }),

        html.Button(
            id='close-notification',
            children='×',
            n_clicks=0,
            style={
                'position': 'absolute',
                'right': '10px',
                'top': '5px',
                'background': 'none',
                'border': 'none',
                'font-size': '20px',
                'cursor': 'pointer',
                'display': 'none'
            }
        )
    ], style={'max-width': '1200px', 'margin': '0 auto', 'padding': '20px'})