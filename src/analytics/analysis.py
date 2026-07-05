from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.translation import get_text, normalize_language


def build_payment_model(summary: pd.DataFrame) -> pd.DataFrame:
    model_df = summary[summary["has_paid"]].copy()
    model_df = model_df[
        ["paid_on_time", "amount_log", "time_to_due_hours", "created_hour", "created_dow", "created_month"]
    ].dropna()
    model_df["paid_on_time"] = model_df["paid_on_time"].astype(int)

    numeric_features = ["amount_log", "time_to_due_hours", "created_hour"]
    categorical_features = ["created_dow", "created_month"]
    X = model_df[["amount_log", "time_to_due_hours", "created_hour", "created_dow", "created_month"]]
    y = model_df["paid_on_time"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    pipeline = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", LogisticRegression(max_iter=2000, class_weight="balanced")),
        ]
    )
    pipeline.fit(X, y)

    feature_names = pipeline.named_steps["preprocess"].get_feature_names_out()
    coefficients = pipeline.named_steps["model"].coef_[0]
    coef_df = pd.DataFrame({"feature": feature_names, "coefficient": coefficients})
    coef_df["abs_coefficient"] = coef_df["coefficient"].abs()
    return coef_df.sort_values("abs_coefficient", ascending=False).head(10)


def build_summary_tables(summary: pd.DataFrame) -> dict[str, pd.DataFrame]:
    total_invoices = len(summary)
    paid_invoices = int(summary["has_paid"].sum())
    late_paid_invoices = int(summary["paid_late"].sum())
    reversed_invoices = int(summary["reversed"].sum())

    overall = pd.DataFrame(
        [
            {"Metric": "Invoices analyzed", "Value": f"{total_invoices:,}"},
            {"Metric": "Paid invoices", "Value": f"{paid_invoices:,} ({paid_invoices / total_invoices * 100:.1f}%)"},
            {
                "Metric": "Invoices paid after due date",
                "Value": f"{late_paid_invoices:,} ({late_paid_invoices / total_invoices * 100:.1f}% of all invoices; {late_paid_invoices / paid_invoices * 100:.1f}% of paid invoices)",
            },
            {"Metric": "Reversed invoices", "Value": f"{reversed_invoices:,} ({reversed_invoices / total_invoices * 100:.3f}%)"},
            {"Metric": "Median reversal delay", "Value": f"{summary['reversal_delay_hours'].median():.1f} hours"},
        ]
    )

    monthly = (
        summary.groupby("created_month")
        .agg(total_invoices=("invoiceId", "count"), paid=("has_paid", "sum"), paid_late=("paid_late", "sum"))
        .reset_index()
    )
    monthly["paid_rate"] = monthly["paid"] / monthly["total_invoices"] * 100
    monthly["late_rate"] = monthly["paid_late"] / monthly["total_invoices"] * 100
    monthly = monthly[monthly["total_invoices"] >= 100].copy()

    amount_bins = pd.qcut(summary["amount"].fillna(0), q=4, labels=["Low", "Medium", "High", "Very high"])
    amount_summary = (
        pd.DataFrame({"amount_bucket": amount_bins, "paid_on_time": summary["paid_on_time"]})
        .groupby("amount_bucket")
        .agg(paid_on_time_rate=("paid_on_time", "mean"), invoice_count=("paid_on_time", "size"))
        .reset_index()
    )

    due_gap_bins = pd.cut(
        summary["time_to_due_hours"].clip(lower=0),
        bins=[0, 1, 3, 7, 30, 1000],
        labels=["<1h", "1-3h", "3-7h", "7-30h", ">30h"],
        include_lowest=True,
    )
    due_gap_summary = (
        pd.DataFrame({"due_gap_bucket": due_gap_bins, "paid_on_time": summary["paid_on_time"]})
        .groupby("due_gap_bucket")
        .agg(paid_on_time_rate=("paid_on_time", "mean"), invoice_count=("paid_on_time", "size"))
        .reset_index()
    )

    reversal_summary = (
        pd.DataFrame({"due_gap_bucket": due_gap_bins, "reversed": summary["reversed"]})
        .groupby("due_gap_bucket")
        .agg(reversal_rate=("reversed", "mean"), invoice_count=("reversed", "size"))
        .reset_index()
    )

    return {
        "overall": overall,
        "monthly": monthly,
        "amount_summary": amount_summary,
        "due_gap_summary": due_gap_summary,
        "reversal_summary": reversal_summary,
    }


def build_executive_summary(
    summary: pd.DataFrame,
    activity: dict[str, Any],
    tables: dict[str, pd.DataFrame],
    model_coefs: pd.DataFrame,
    language: str = "US",
) -> list[dict[str, str]]:
    lang = normalize_language(language)
    total_invoices = len(summary)
    paid_invoices = int(summary["has_paid"].sum())
    late_paid_invoices = int(summary["paid_late"].sum())
    reversed_invoices = int(summary["reversed"].sum())
    median_delay = float(summary["reversal_delay_hours"].median())

    monthly = tables["monthly"].copy()
    month_col = next(
        (col for col in monthly.columns if col in {"created_month", "Created month", "Mês de criação"}),
        None,
    )
    late_rate_col = next(
        (col for col in monthly.columns if col in {"late_rate", "Late rate", "Taxa de atraso"}),
        None,
    )
    if month_col is None or late_rate_col is None:
        raise KeyError("created_month")
    monthly[month_col] = monthly[month_col].astype(str)
    late_trend = ", ".join(
        f"{row[month_col]}: {row[late_rate_col]:.2f}%"
        for _, row in monthly.iterrows()
    )

    amount_summary = tables["amount_summary"].copy()
    due_gap_summary = tables["due_gap_summary"].copy()

    amount_bucket_col = next(
        (col for col in amount_summary.columns if col in {"amount_bucket", "Faixa de valor", "Amount bucket"}),
        None,
    )
    amount_rate_col = next(
        (col for col in amount_summary.columns if col in {"paid_on_time_rate", "Taxa de pagamento no prazo", "On-time payment rate"}),
        None,
    )
    due_gap_bucket_col = next(
        (col for col in due_gap_summary.columns if col in {"due_gap_bucket", "Faixa de diferença para o vencimento", "Due-gap bucket"}),
        None,
    )
    due_gap_rate_col = next(
        (col for col in due_gap_summary.columns if col in {"paid_on_time_rate", "Taxa de pagamento no prazo", "On-time payment rate"}),
        None,
    )
    if amount_bucket_col is None or amount_rate_col is None or due_gap_bucket_col is None or due_gap_rate_col is None:
        raise KeyError("paid_on_time_rate")

    best_dow, best_hour = activity["best_window"]
    best_amount_bucket = amount_summary.sort_values(amount_rate_col).iloc[0][amount_bucket_col]
    best_due_gap = due_gap_summary.sort_values(due_gap_rate_col).iloc[0][due_gap_bucket_col]

    if lang == "PT":
        return [
            {
                "title": get_text("best_deployment_title", lang),
                "value": f"{best_dow} às {best_hour:02d}:00 é a janela de menor atividade ({activity['best_window_events']} eventos).",
            },
            {
                "title": get_text("payment_conversion_title", lang),
                "value": f"{paid_invoices / total_invoices * 100:.1f}% das faturas são pagas; {late_paid_invoices / total_invoices * 100:.1f}% são pagas após o vencimento.",
            },
            {
                "title": get_text("payment_drivers_title", lang),
                "value": f"As faturas têm mais probabilidade de serem pagas no prazo quando a janela até o vencimento é curta e o valor da fatura está em uma faixa menor; o modelo também mostra que a hora, o dia e o mês de criação influenciam o prazo. O padrão mais forte observado é que {best_due_gap} e {best_amount_bucket} estão associados a taxas menores de pagamento no prazo.",
            },
            {
                "title": get_text("overdue_trend_title", lang),
                "value": f"Taxa de pagamentos atrasados por mês: {late_trend}.",
            },
            {
                "title": get_text("reversal_rate_title", lang),
                "value": f"{reversed_invoices / total_invoices * 100:.3f}% das faturas são revertidas (parcial ou totalmente, com base nos eventos de reversão do conjunto de dados).",
            },
            {
                "title": get_text("reversal_timing_title", lang),
                "value": f"A reversão típica ocorre após {median_delay:.1f} horas; o conjunto de dados não contém um rótulo separado para reversão parcial/total, então este resumo usa eventos de reversão como um único grupo.",
            },
        ]

    return [
        {
            "title": get_text("best_deployment_title", lang),
            "value": f"{best_dow} at {best_hour:02d}:00 is the lowest-activity window ({activity['best_window_events']} events).",
        },
        {
            "title": get_text("payment_conversion_title", lang),
            "value": f"{paid_invoices / total_invoices * 100:.1f}% of invoices are paid; {late_paid_invoices / total_invoices * 100:.1f}% are paid after the due date.",
        },
        {
            "title": get_text("payment_drivers_title", lang),
            "value": f"Invoices are more likely to be paid on time when the due window is short and the invoice amount is in a lower bucket; the model also shows that creation hour/day/month influence timing. The strongest observed pattern is that {best_due_gap} and {best_amount_bucket} are associated with lower on-time payment rates.",
        },
        {
            "title": get_text("overdue_trend_title", lang),
            "value": f"Late-payment rate by month: {late_trend}.",
        },
        {
            "title": get_text("reversal_rate_title", lang),
            "value": f"{reversed_invoices / total_invoices * 100:.3f}% of invoices are reversed (partial or total, based on reversal events in the dataset).",
        },
        {
            "title": get_text("reversal_timing_title", lang),
            "value": f"The typical reversal happens after {median_delay:.1f} hours; the dataset does not contain a separate partial/total label, so this summary uses reversal events as a combined bucket.",
        },
    ]
