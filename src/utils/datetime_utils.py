from __future__ import annotations

import pandas as pd


def parse_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for column in ["invoiceCreated", "logCreated", "invoiceDue"]:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], format="mixed")
    return df
