from .data_callbacks import register_data_callbacks
from .graph_callbacks import register_graph_callbacks

def register_callbacks(app):
    register_data_callbacks(app)
    register_graph_callbacks(app)