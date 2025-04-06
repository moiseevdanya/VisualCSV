from dash import html


def create_notification(message):
    return html.Div([
        html.Button('×',
                    id='close-notification',
                    n_clicks=0,
                    style={
                        'float': 'right',
                        'background': 'none',
                        'border': 'none',
                        'cursor': 'pointer',
                        'font-size': '16px'
                    }),
        html.P(message, style={'margin': '0'})
    ])
