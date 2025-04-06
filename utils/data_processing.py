import base64
import csv
import io
import logging

import numpy as np
import pandas as pd
from prophet import Prophet
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def validate_dataframe(df: pd.DataFrame) -> None:
    """Проверка качества данных перед построением графиков."""
    if df.empty:
        raise ValueError("Файл не содержит данных")
    if df.isnull().values.any():
        logger.warning("Обнаружены пропущенные значения в данных")


def parse_csv_with_commas(content):
    """Обработка CSV с запятыми в полях"""
    rows = []
    reader = csv.reader(io.StringIO(content), quotechar='"')
    for row in reader:
        if len(row) > 4:
            fixed_row = row[:3] + [', '.join(row[3:])]
            rows.append(fixed_row)
        else:
            rows.append(row)
    return pd.DataFrame(rows[1:], columns=rows[0])


def process_uploaded_file(contents: str) -> pd.DataFrame:
    """Основная функция обработки загруженного файла."""
    if contents is None:
        raise ValueError("Не получены данные файла")

    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        if 'csv' in content_type:
            try:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            except pd.errors.ParserError:
                df = parse_csv_with_commas(decoded.decode('utf-8'))
        elif 'xls' in content_type:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            raise ValueError("Неподдерживаемый формат файла")

        validate_dataframe(df)  # Добавляем валидацию
        return df

    except Exception as e:
        logger.error(f"Ошибка обработки файла: {e}", exc_info=True)
        raise ValueError(f"Ошибка обработки файла: {str(e)}")


def detect_anomalies(df, column):
    """Обнаружение аномалий в указанной колонке"""
    model = IsolationForest(contamination=0.05)
    df['anomaly'] = model.fit_predict(df[[column]])
    df['anomaly'] = df['anomaly'].map({1: 0, -1: 1})  # 1=аномалия
    return df


def forecast_time_series(df, date_col, value_col, periods=30):
    """Прогнозирование временных рядов"""
    df = df.rename(columns={date_col: 'ds', value_col: 'y'})
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast


def cluster_data(df, n_clusters=3):
    """Кластеризация данных"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    kmeans = KMeans(n_clusters=n_clusters)
    df['cluster'] = kmeans.fit_predict(df[numeric_cols])
    return df
