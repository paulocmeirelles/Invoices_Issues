from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "report_outputs"
FIG_DIR = OUTPUT_DIR / "figures"


def save_chart(path: Path, fig: plt.Figure) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def create_visuals(summary: pd.DataFrame, activity: dict[str, object], tables: dict[str, pd.DataFrame]) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 4))
    activity["hourly"].plot(kind="bar", ax=ax, color="#4C78A8")
    ax.set_title("Invoice activity by hour of day")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Log events")
    ax.set_xticks(range(0, 24, 2))
    save_chart(FIG_DIR / "activity_by_hour.png", fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(data=tables["amount_summary"], x="amount_bucket", y="paid_on_time_rate", ax=ax, color="#4C78A8")
    ax.set_title("On-time payment rate by invoice amount bucket")
    ax.set_xlabel("Amount bucket")
    ax.set_ylabel("On-time payment rate")
    save_chart(FIG_DIR / "payment_by_amount.png", fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(data=tables["due_gap_summary"], x="due_gap_bucket", y="paid_on_time_rate", ax=ax, color="#54a24b")
    ax.set_title("On-time payment rate by due-gap bucket")
    ax.set_xlabel("Due-gap bucket")
    ax.set_ylabel("On-time payment rate")
    save_chart(FIG_DIR / "payment_by_due_gap.png", fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    tables["monthly"].plot(x="created_month", y="late_rate", ax=ax, marker="o", color="#e45756")
    ax.set_title("Late payment rate by month")
    ax.set_xlabel("Invoice creation month")
    ax.set_ylabel("Late payment rate (%)")
    save_chart(FIG_DIR / "late_rate_by_month.png", fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    summary["reversal_delay_hours"].dropna().hist(bins=25, ax=ax, color="#72b7b2")
    ax.set_title("Distribution of reversal delay")
    ax.set_xlabel("Hours until reversal")
    ax.set_ylabel("Invoices")
    save_chart(FIG_DIR / "reversal_delay.png", fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(data=tables["reversal_summary"], x="due_gap_bucket", y="reversal_rate", ax=ax, color="#e45756")
    ax.set_title("Reversal rate by due-gap bucket")
    ax.set_xlabel("Due-gap bucket")
    ax.set_ylabel("Reversal rate")
    save_chart(FIG_DIR / "reversal_by_due_gap.png", fig)
