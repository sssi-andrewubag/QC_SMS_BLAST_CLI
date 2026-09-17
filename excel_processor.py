import os
from typing import Any, Union
import pandas as pd
from phone_utils import process_phone_numbers, ExtractionResult

def load_excel_numbers(
    file_path: str,
    col_identifier: Union[int, str] = 6,
    sheet_name: Union[int, str] = 0
) -> ExtractionResult:
    """
    Loads phone numbers from an Excel file column.
    
    :param file_path: Path to .xlsx or .xls file
    :param col_identifier: 1-based column index (e.g. 6) or column header name (e.g. "mobile no")
    :param sheet_name: Sheet index (0) or sheet name string
    :return: ExtractionResult containing categorized phone numbers
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Excel file not found: {file_path}")

    # Read dataframe
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    if df.empty:
        return ExtractionResult()

    # Determine column series
    if isinstance(col_identifier, int):
        col_idx = col_identifier - 1  # Convert 1-based to 0-based index
        if col_idx < 0 or col_idx >= len(df.columns):
            raise ValueError(
                f"Column index {col_identifier} is out of bounds for Excel file with {len(df.columns)} columns."
            )
        target_series = df.iloc[:, col_idx]
    elif isinstance(col_identifier, str):
        # Match column by header name (case-insensitive)
        matched_col = None
        for col in df.columns:
            if str(col).strip().lower() == col_identifier.strip().lower():
                matched_col = col
                break
        if matched_col is None:
            raise ValueError(
                f"Column '{col_identifier}' not found in Excel file headers: {list(df.columns)}"
            )
        target_series = df[matched_col]
    else:
        raise TypeError("col_identifier must be an int (1-based index) or a str (column name)")

    raw_values = target_series.tolist()
    return process_phone_numbers(raw_values)
