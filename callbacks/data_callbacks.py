from dash import dash_table
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

from utils.data_processing import process_uploaded_file


def register_data_callbacks(app):
    """
    Регистрирует все callback'ы, связанные с обработкой данных, в Dash приложении.

    Args:
        app (dash.Dash): Экземпляр Dash приложения, к которому будут добавлены callback'ы

    Callbacks:
        Регистрирует один основной callback, который обрабатывает:
        - Отображение загруженных данных в таблице
        - Обновление опций для выбора осей X, Y, Z
    """

    @app.callback(
        [Output('output-data-upload', 'children'),
         Output('x-axis', 'options'),
         Output('y-axis', 'options'),
         Output('z-axis', 'options')],
        [Input('upload-data', 'contents')],
        prevent_initial_call=True
    )
    def update_data_display(contents):
        """
        Обрабатывает загруженные данные и обновляет интерфейс.

        Args:
            contents (str | None): Содержимое загруженного файла в base64 кодировке или None,
                                если файл не был загружен

        Returns:
            tuple: Кортеж из 4 элементов:
                - dash_table.DataTable | html.Div: Таблица с данными или сообщение об ошибке
                - list: Список опций для оси X в формате [{'label': str, 'value': str}]
                - list: Список опций для оси Y в формате [{'label': str, 'value': str}]
                - list: Список опций для оси Z в формате [{'label': str, 'value': str}]

        Raises:
            PreventUpdate: Если contents равен None (файл не загружен)

        Processing Logic:
            1. Проверяет наличие загруженных данных
            2. Парсит файл с помощью process_uploaded_file()
            3. Создает DataTable для отображения данных
            4. Генерирует опции для выбора осей
            5. В случае ошибки возвращает сообщение и пустые списки опций
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

            return table, options, options, options

        except Exception as e:
            return html.Div(f"Ошибка: {str(e)}"), [], [], []
