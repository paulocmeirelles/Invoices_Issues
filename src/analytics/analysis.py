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
    model_df = model_df[["paid_on_time", "amount_log", "time_to_due_hours", "created_hour", "created_dow"]].dropna()
    model_df["paid_on_time"] = model_df["paid_on_time"].astype(int)

    numeric_features = ["amount_log", "time_to_due_hours", "created_hour"]
    categorical_features = ["created_dow"]
    X = model_df[["amount_log", "time_to_due_hours", "created_hour", "created_dow"]]
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


def build_reversal_model(summary: pd.DataFrame) -> pd.DataFrame:
    model_df = summary[["reversed", "amount_log", "time_to_due_hours", "created_hour", "created_dow"]].copy()
    model_df = model_df.dropna()
    model_df["reversed"] = model_df["reversed"].astype(int)

    numeric_features = ["amount_log", "time_to_due_hours", "created_hour"]
    categorical_features = ["created_dow"]
    X = model_df[["amount_log", "time_to_due_hours", "created_hour", "created_dow"]]
    y = model_df["reversed"]

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


def build_reversal_amount_summary(summary: pd.DataFrame, quantiles: tuple[float, ...] = (0.25, 0.5, 0.75)) -> pd.DataFrame:
    if summary.empty or "amount" not in summary.columns or "reversed" not in summary.columns:
        return pd.DataFrame(columns=["threshold", "below_rate", "above_rate", "rate_delta", "below_count", "above_count"])

    amount = pd.to_numeric(summary["amount"], errors="coerce").fillna(0)
    rows: list[dict[str, float | int]] = []

    for quantile in quantiles:
        threshold = float(amount.quantile(quantile))
        if pd.isna(threshold):
            continue

        below_mask = amount <= threshold
        above_mask = amount > threshold
        below_count = int(below_mask.sum())
        above_count = int(above_mask.sum())
        if below_count < 2 or above_count < 2:
            continue

        below_rate = float(summary.loc[below_mask, "reversed"].mean() * 100)
        above_rate = float(summary.loc[above_mask, "reversed"].mean() * 100)
        rows.append(
            {
                "threshold": round(threshold, 2),
                "below_rate": below_rate,
                "above_rate": above_rate,
                "rate_delta": below_rate - above_rate,
                "below_count": below_count,
                "above_count": above_count,
            }
        )

    if not rows:
        return pd.DataFrame(columns=["threshold", "below_rate", "above_rate", "rate_delta", "below_count", "above_count"])

    summary_df = pd.DataFrame(rows)
    summary_df["abs_rate_delta"] = summary_df["rate_delta"].abs()
    return summary_df.sort_values("abs_rate_delta", ascending=False).reset_index(drop=True)


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

    amount_bins, amount_ranges = pd.qcut(summary["amount"].fillna(0), q=4, labels=["Low", "Medium", "High", "Very high"], retbins=True)
    amount_summary = (
        pd.DataFrame({"amount_bucket": amount_bins, "paid_on_time": summary["paid_on_time"]})
        .groupby("amount_bucket")
        .agg(paid_on_time_rate=("paid_on_time", "mean"), invoice_count=("paid_on_time", "size"))
        .reset_index()
    )
    labels = ["Low", "Medium", "High", "Very high"]
    ranges_dict = {}
    for i, label in enumerate(labels):
        ranges_dict[label] = f"RS{amount_ranges[i]:,.2f} - RS{amount_ranges[i+1]:,.2f}"
    amount_summary.attrs["ranges_dict"] = ranges_dict
    low_range_str = f"RS{amount_ranges[0]:,.2f} - RS{amount_ranges[1]:,.2f}"
    amount_summary.attrs["low_range"] = low_range_str

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
    reversal_amount_summary = build_reversal_amount_summary(summary)

    return {
        "overall": overall,
        "monthly": monthly,
        "amount_summary": amount_summary,
        "due_gap_summary": due_gap_summary,
        "reversal_summary": reversal_summary,
        "reversal_amount_summary": reversal_amount_summary,
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
    median_delay_str = f"{int(median_delay)}h{round((median_delay - int(median_delay)) * 60):02d}min"

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
    reversal_amount_summary = tables.get("reversal_amount_summary", pd.DataFrame()).copy()

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
    if lang == "PT":
        best_dow = get_text(best_dow.lower(), lang)
    best_amount_bucket = amount_summary.sort_values(amount_rate_col).iloc[-1][amount_bucket_col]
    ranges_dict = tables["amount_summary"].attrs.get("ranges_dict", {})
    best_amount_range_str = ranges_dict.get(best_amount_bucket, str(best_amount_bucket))
    best_due_gap = due_gap_summary.sort_values(due_gap_rate_col).iloc[0][due_gap_bucket_col]
    worst_due_gap = due_gap_summary.sort_values(due_gap_rate_col, ascending=False).iloc[0][due_gap_bucket_col]

    reversal_insight = []
    if not reversal_amount_summary.empty:
        best_threshold = reversal_amount_summary.sort_values("abs_rate_delta", ascending=False).iloc[0]
        threshold_value = float(best_threshold["threshold"])
        below_rate = float(best_threshold["below_rate"])
        above_rate = float(best_threshold["above_rate"])
        if lang == "PT":
            comparison = f"cai para {above_rate:.1f}%" if above_rate < below_rate else f"sobe para {above_rate:.1f}%"
            reversal_insight = [{
                "title": get_text("reversal_amount_title", lang),
                "value": f"Faturas até RS{threshold_value:,.0f} têm taxa de reversão de {below_rate:.1f}%; acima desse limite, a taxa {comparison}.",
            }]
        else:
            comparison = f"drops to {above_rate:.1f}%" if above_rate < below_rate else f"rises to {above_rate:.1f}%"
            reversal_insight = [{
                "title": get_text("reversal_amount_title", lang),
                "value": f"Invoices up to RS{threshold_value:,.0f} show a reversal rate of {below_rate:.1f}%; above that threshold, the rate {comparison}.",
            }]

    if lang == "PT":
        return [
            {
                "title": get_text("best_deployment_title", lang),
                "value": f"{best_dow} por volta de {best_hour:02d}:00 é a janela de menor atividade ({activity['best_window_events']} eventos).\nMotivo: Temos baixo volume de tráfego, o que nos proporciona tempo suficiente para reverter a alteração caso ocorra algum problema, minimizando o impacto para os usuários.",
            },
            {
                "title": get_text("payment_conversion_title", lang),
                "value": f"{paid_invoices / total_invoices * 100:.1f}% das faturas são pagas; {late_paid_invoices / total_invoices * 100:.1f}% são pagas após o vencimento.",
            },
            {
                "title": get_text("payment_drivers_title", lang),
                "value": f"As faturas têm mais probabilidade de serem pagas no prazo quando a janela até o vencimento é curta ({worst_due_gap}) e o valor da fatura está em uma faixa menor ({amount_summary.attrs['low_range']}); o modelo também mostra que a hora, o dia e o mês de criação influenciam o prazo. O padrão mais forte observado é que {best_due_gap} e {best_amount_bucket} ({best_amount_range_str}) estão associados a taxas menores de pagamento no prazo.",
            },
            {
                "title": get_text("overdue_trend_title", lang),
                "value": f"Taxa de pagamentos atrasados por mês: {late_trend}.",
            },
            {
                "title": get_text("reversal_rate_title", lang),
                "value": f"{reversed_invoices / total_invoices * 100:.3f}% das faturas são revertidas (parcial ou totalmente, com base nos eventos de reversão do conjunto de dados).",
            },
            *reversal_insight,
            {
                "title": get_text("reversal_timing_title", lang),
                "value": f"A reversão típica ocorre após {median_delay_str}.",
            },
        ]

    return [
        {
            "title": get_text("best_deployment_title", lang),
            "value": f"{best_dow} around of {best_hour:02d}:00 is the lowest-activity window ({activity['best_window_events']} events).\nReason: Low traffic provides enough time to perform a rollback should any issues occur, minimizing the overall impact.",
        },
        {
            "title": get_text("payment_conversion_title", lang),
            "value": f"{paid_invoices / total_invoices * 100:.1f}% of invoices are paid; {late_paid_invoices / total_invoices * 100:.1f}% are paid after the due date.",
        },
        {
            "title": get_text("payment_drivers_title", lang),
            "value": f"Invoices are more likely to be paid on time when the due window is short ({worst_due_gap}) and the invoice amount is in a lower bucket ({amount_summary.attrs['low_range']}); the model also shows that creation hour/day/month influence timing. The strongest observed pattern is that {best_due_gap} and {best_amount_bucket} ({best_amount_range_str}) are associated with lower on-time payment rates.",
        },
        {
            "title": get_text("overdue_trend_title", lang),
            "value": f"Late-payment rate by month: {late_trend}.",
        },
        {
            "title": get_text("reversal_rate_title", lang),
            "value": f"{reversed_invoices / total_invoices * 100:.3f}% of invoices are reversed (partial or total, based on reversal events in the dataset).",
        },
        *reversal_insight,
        {
            "title": get_text("reversal_timing_title", lang),
            "value": f"The typical reversal happens after {median_delay_str}.",
        },
    ]
