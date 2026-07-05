from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.utils import parse_datetime_columns

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "InvoiceLog Dataset.csv"
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def build_invoice_summary(df: pd.DataFrame) -> pd.DataFrame:
    df = parse_datetime_columns(df)

    aggregate_columns = {
        "created": ("invoiceCreated", "min"),
        "due": ("invoiceDue", "min"),
        "amount": ("amount", "max"),
    }
    if "logId" in df.columns:
        aggregate_columns["log_count"] = ("logId", "count")
    else:
        aggregate_columns["log_count"] = ("invoiceId", "count")

    invoice_summary = df.groupby("invoiceId", as_index=False).agg(**aggregate_columns)

    paid_times = (
        df.loc[df["type"] == "paid"]
        .groupby("invoiceId", as_index=False)["logCreated"]
        .min()
        .rename(columns={"logCreated": "paid_at"})
    )
    reversal_times = (
        df.loc[df["type"].isin(["reversed", "reversing"])]
        .groupby("invoiceId", as_index=False)["logCreated"]
        .min()
        .rename(columns={"logCreated": "reversal_at"})
    )

    invoice_summary = invoice_summary.merge(paid_times, on="invoiceId", how="left")
    invoice_summary = invoice_summary.merge(reversal_times, on="invoiceId", how="left")

    invoice_summary["has_paid"] = invoice_summary["paid_at"].notna()
    invoice_summary["paid_on_time"] = invoice_summary["has_paid"] & (
        invoice_summary["paid_at"] <= invoice_summary["due"]
    )
    invoice_summary["paid_late"] = invoice_summary["has_paid"] & ~invoice_summary["paid_on_time"]
    invoice_summary["reversed"] = invoice_summary["reversal_at"].notna()
    invoice_summary["reversal_delay_hours"] = (
        (invoice_summary["reversal_at"] - invoice_summary["created"]).dt.total_seconds() / 3600
    )
    invoice_summary["time_to_due_hours"] = (
        (invoice_summary["due"] - invoice_summary["created"]).dt.total_seconds() / 3600
    )
    invoice_summary["created_month"] = invoice_summary["created"].dt.to_period("M").astype(str)
    invoice_summary["created_dow"] = invoice_summary["created"].dt.day_name()
    invoice_summary["created_hour"] = invoice_summary["created"].dt.hour
    invoice_summary["amount_log"] = np.log1p(invoice_summary["amount"])
    return invoice_summary


def summarize_activity(df: pd.DataFrame) -> dict[str, Any]:
    df = parse_datetime_columns(df)
    activity = df.copy()
    activity["dow"] = activity["logCreated"].dt.day_name()
    activity["hour"] = activity["logCreated"].dt.hour

    hourly = activity.groupby("hour").size().reindex(range(24), fill_value=0)
    daily = activity.groupby("dow").size().reindex(DAY_ORDER, fill_value=0)
    combo = (
        activity.groupby(["dow", "hour"]).size().reset_index(name="events").sort_values(["dow", "hour"])
    )
    best_window = combo.sort_values("events").iloc[0]

    return {
        "hourly": hourly,
        "daily": daily,
        "combo": combo,
        "best_window": (best_window["dow"], int(best_window["hour"])),
        "best_window_events": int(best_window["events"]),
    }
