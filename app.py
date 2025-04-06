from dash import Dash

from callbacks import register_callbacks
from components.layout import create_layout

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "CSV/Excel Визуализатор"
app.layout = create_layout()
register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True, port=8050)