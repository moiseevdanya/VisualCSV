import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

from utils.data_processing import process_uploaded_file


def register_graph_callbacks(app):
    """
    Регистрирует все callback'ы, связанные с построением графиков, в Dash приложении.

    Args:
        app (dash.Dash): Экземпляр Dash приложения, к которому будут добавлены callback'ы

    Callbacks:
        Регистрирует основной callback, который:
        1. Обрабатывает выбор типа графика и осей
        2. Строит соответствующий график с помощью Plotly
        3. Управляет отображением уведомлений об ошибках
    """

    @app.callback(
        [Output('graph', 'figure'),
         Output('notification', 'children'),
         Output('notification', 'style'),
         Output('close-notification', 'style')],
        [Input('graph-type', 'value'),
         Input('x-axis', 'value'),
         Input('y-axis', 'value'),
         Input('z-axis', 'value'),
         Input('upload-data', 'contents'),
         Input('close-notification', 'n_clicks')],
        prevent_initial_call=True
    )
    def update_graph(graph_type, x_axis, y_axis, z_axis, contents):
        """
        Основной callback для построения графиков и обработки взаимодействий.

        Args:
            graph_type (str): Тип графика из выпадающего списка
            x_axis (str): Выбранная колонка для оси X
            y_axis (str): Выбранная колонка для оси Y
            z_axis (str): Выбранная колонка для оси Z (для 3D графиков)
            contents (str): Содержимое загруженного файла в base64

        Returns:
            tuple: Кортеж из 4 элементов:
                - figure: Объект графика Plotly
                - str: Текст уведомления об ошибке (или None)
                - dict: Стили для уведомления
                - dict: Стили для кнопки закрытия уведомления
        """
        ctx = dash.callback_context
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Обработка закрытия уведомления
        if trigger_id == 'close-notification':
            return dash.no_update, None, {'display': 'none'}, {'display': 'none'}

        # Проверка наличия данных
        if not contents:
            raise PreventUpdate

        try:
            df = process_uploaded_file(contents)

            # Базовые проверки
            if not x_axis or (graph_type not in ['histogram', 'pie'] and not y_axis):
                raise PreventUpdate

            # Построение графиков
            if graph_type == 'line':
                fig = px.line(df, x=x_axis, y=y_axis, title='Линейный график')
            elif graph_type == 'bar':
                fig = px.bar(df, x=x_axis, y=y_axis, title='Столбчатая диаграмма')
            elif graph_type == 'pie':
                if not x_axis:
                    return dash.no_update, "Для круговой диаграммы нужно выбрать категории (ось X)", {
                        'display': 'block'}, {'display': 'block'}

                # Если y_axis не указан, считаем количество каждой категории
                if not y_axis:
                    pie_data = df[x_axis].value_counts().reset_index()
                    pie_data.columns = ['category', 'count']
                    fig = px.pie(pie_data,
                                 names='category',
                                 values='count',
                                 title=f'Распределение по {x_axis} (количество)')
                else:
                    # Если y_axis указан, используем его значения (любого типа)
                    pie_df = df[[x_axis, y_axis]].dropna()

                    if len(pie_df) == 0:
                        return dash.no_update, "Нет данных для построения диаграммы", {'display': 'block'}, {
                            'display': 'block'}

                    # Для нечисловых значений преобразуем в строки и считаем количество
                    if not pd.api.types.is_numeric_dtype(pie_df[y_axis]):
                        pie_data = pie_df.groupby([x_axis, y_axis]).size().reset_index(name='count')
                        fig = px.pie(pie_data,
                                     names=y_axis,
                                     values='count',
                                     title=f'Распределение {y_axis} по {x_axis}',
                                     color=x_axis)
                    else:
                        # Для числовых значений используем как есть
                        fig = px.pie(pie_df,
                                     names=x_axis,
                                     values=y_axis,
                                     title=f'Распределение {y_axis} по {x_axis}')

                # Улучшаем отображение
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide',
                                  legend=dict(orientation="h", yanchor="bottom", y=-0.2))
            elif graph_type == 'scatter':
                fig = px.scatter(df, x=x_axis, y=y_axis, title='Точечная диаграмма')
            elif graph_type == 'histogram':
                fig = px.histogram(df, x=x_axis, title='Гистограмма')
            elif graph_type == 'box':
                fig = px.box(df, x=x_axis, y=y_axis, title='Ящик с усами')
            elif graph_type == 'heatmap':
                if not x_axis or not y_axis:
                    return dash.no_update, "Для тепловой карты нужны X и Y оси", {'display': 'block'}, {
                        'display': 'block'}
                fig = px.density_heatmap(df, x=x_axis, y=y_axis, title='Тепловая карта')
            elif graph_type == 'bubble':
                if not x_axis or not y_axis:
                    return dash.no_update, "Для пузырьковой диаграммы нужны X и Y оси", {'display': 'block'}, {
                        'display': 'block'}

                # Проверяем, есть ли числовая колонка для размера пузырьков
                numeric_cols = df.select_dtypes(include=['number']).columns
                size_col = z_axis if z_axis in numeric_cols else (
                    numeric_cols[2] if len(numeric_cols) > 2 else None
                )

                # Если нет подходящей колонки для размера, используем постоянный размер
                if size_col is None:
                    fig = px.scatter(df, x=x_axis, y=y_axis,
                                     title='Пузырьковая диаграмма (постоянный размер)')
                else:
                    # Нормализуем размер для лучшего отображения
                    sizes = (df[size_col] - df[size_col].min()) / (df[size_col].max() - df[size_col].min()) * 100 + 10
                    fig = px.scatter(df, x=x_axis, y=y_axis, size=sizes,
                                     title=f'Пузырьковая диаграмма (размер: {size_col})')

                # Настраиваем внешний вид
                fig.update_traces(marker=dict(opacity=0.7, line=dict(width=0.5, color='DarkSlateGrey')))
            elif graph_type == 'sankey':
                if not x_axis or not y_axis:
                    return dash.no_update, "Для диаграммы Санкея нужны источник и цель", {'display': 'block'}, {
                        'display': 'block'}

                # Группируем данные для подсчета потоков
                df_sankey = df.groupby([x_axis, y_axis]).size().reset_index(name='value')

                # Создаем словарь узлов
                unique_nodes = pd.unique(df[[x_axis, y_axis]].values.ravel('K'))
                node_dict = {node: i for i, node in enumerate(unique_nodes)}

                fig = go.Figure(go.Sankey(
                    node=dict(
                        label=list(node_dict.keys()),
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5)
                    ),
                    link=dict(
                        source=df_sankey[x_axis].map(node_dict),
                        target=df_sankey[y_axis].map(node_dict),
                        value=df_sankey['value'].tolist(),
                        color="rgba(0,128,0,0.3)"
                    )
                ))
                fig.update_layout(title_text='Диаграмма Санкея', font_size=10)
            elif graph_type == 'choropleth':
                if not x_axis:
                    return dash.no_update, "Для карты нужна колонка с географическими данными", {'display': 'block'}, {
                        'display': 'block'}
                fig = px.choropleth(df, locations=x_axis, locationmode='country names',
                                    color=y_axis if y_axis else df.columns[1],
                                    title='Географическая карта')
            elif graph_type == 'gantt':
                if not all(col in df.columns for col in ['Task', 'Start', 'Finish']):
                    return dash.no_update, "Для графика Ганта нужны колонки: Task, Start, Finish", {
                        'display': 'block'}, {'display': 'block'}
                fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", title='График Ганта')
            elif graph_type == 'candlestick':
                if not all(col in df.columns for col in ['open', 'high', 'low', 'close']):
                    return dash.no_update, "Для биржевого графика нужны колонки: open, high, low, close", {
                        'display': 'block'}, {'display': 'block'}
                fig = go.Figure(go.Candlestick(
                    x=df[x_axis] if x_axis else df.index,
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close']
                ))
            elif graph_type == 'combo':
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df[x_axis], y=df[y_axis], name='Линия'))
                fig.add_trace(go.Bar(x=df[x_axis], y=df[y_axis], name='Столбцы'))
                fig.update_layout(title='Комбинированная диаграмма')
            else:
                fig = px.scatter(title='Выберите тип графика')

            return fig, None, {'display': 'none'}, {'display': 'none'}

        except Exception as e:
            return px.scatter(title='Ошибка'), str(e), {'display': 'block'}, {'display': 'block'}
