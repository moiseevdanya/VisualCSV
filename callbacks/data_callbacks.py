from dash import dash_table, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

from utils.data_processing import process_uploaded_file


def register_data_callbacks(app):
    """
    Регистрирует все callback'ы, связанные с обработкой данных, в Dash приложении.
    """

    @app.callback(
        [Output('output-data-upload', 'children'),
         Output('stored-data', 'data'),
         Output('x-axis', 'options'),
         Output('y-axis', 'options'),
         Output('z-axis', 'options')],
        [Input('upload-data', 'contents')],
        prevent_initial_call=True
    )
    def update_data_display(contents):
        """
        Обрабатывает загруженные данные и обновляет интерфейс.
        Возвращает:
        - Таблицу с данными
        - Данные в формате словаря для хранения
        - Опции для осей X, Y, Z
        """
        if not contents:
            raise PreventUpdate

        try:
            df = process_uploaded_file(contents)
            options = [{'label': col, 'value': col} for col in df.columns]

            table = dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': col, 'id': col} for col in df.columns],
                page_size=10,
                style_table={'overflowX': 'auto'}
            )

            # Возвращаем таблицу, данные и опции для осей
            return table, df.to_dict('records'), options, options, options

        except Exception as e:
            # Возвращаем ошибку и пустые списки
            return html.Div(f"Ошибка: {str(e)}"), None, [], [], []
