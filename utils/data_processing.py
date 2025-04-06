import base64
import csv
import io

import pandas as pd


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