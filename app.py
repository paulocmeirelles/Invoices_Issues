from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import build_executive_summary, build_payment_model, build_summary_tables
from src.invoice import DATA_PATH, build_invoice_summary, summarize_activity
from src.translation import get_text, normalize_language, translate_table_for_language


st.set_page_config(page_title="Pix Invoice Analytics", layout="wide")


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def get_language() -> str:
    if "language" not in st.session_state:
        st.session_state["language"] = "US"
    return normalize_language(st.session_state.get("language", "US"))


def translate_tables(tables: dict[str, pd.DataFrame], language: str) -> dict[str, pd.DataFrame]:
    return {name: translate_table_for_language(table, language) for name, table in tables.items()}


def render_metrics(
    all_registers: int,
    summary: pd.DataFrame,
    activity: dict[str, object],
    tables: dict[str, pd.DataFrame],
    model_coefs: pd.DataFrame,
    language: str,
) -> None:
    total = len(summary)
    paid = int(summary["has_paid"].sum())
    late = int(summary["paid_late"].sum())
    reversed_count = int(summary["reversed"].sum())
    median_delay = float(summary["reversal_delay_hours"].median())
    t = lambda key: get_text(key, language)

    left, mid, right, fourth, fifth = st.columns(5)
    left.metric(t("unique_invoices"), f"{total:,}")
    mid.metric(t("paid"), f"{paid:,} ({paid / total * 100:.1f}%)")
    right.metric(t("paid_after_due_date"), f"{late:,} ({late / total * 100:.1f}%)")
    fourth.metric(t("reversed"), f"{reversed_count:,} ({reversed_count / total * 100:.3f}%)")
    fifth.metric(t("total_registers"), f"{all_registers:,}")
    st.caption(f"{t('median_reversal_delay')}: {median_delay:.1f} hours")

    st.subheader(t("executive_summary"))
    exec_summary = build_executive_summary(summary, activity, tables, model_coefs, language=language)
    for item in exec_summary:
        st.write(f"**{item['title']}**: {item['value']}")


def render_charts(
    summary: pd.DataFrame,
    activity: dict[str, object],
    tables: dict[str, pd.DataFrame],
    language: str,
) -> None:
    t = lambda key: get_text(key, language)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(t("activity_by_hour"))
        hourly_df = pd.DataFrame({"hour": activity["hourly"].index, "events": activity["hourly"].values})
        st.plotly_chart(
            px.bar(hourly_df, x="hour", y="events", labels={"hour": t("hour"), "events": t("log_events")}),
            width="stretch",
        )
    with col2:
        st.subheader(t("late_payment_rate_by_month"))
        monthly_df = tables["monthly"].copy()
        st.plotly_chart(
            px.line(
                monthly_df,
                x="created_month",
                y="late_rate",
                labels={"created_month": t("month"), "late_rate": t("late_payment_rate_pct")},
            ),
            width="stretch",
        )

    col3, col4 = st.columns(2)
    with col3:
        st.subheader(t("on_time_rate_by_amount_bucket"))
        amount_df = tables["amount_summary"].copy()
        st.plotly_chart(
            px.bar(
                amount_df,
                x="amount_bucket",
                y="paid_on_time_rate",
                labels={"amount_bucket": t("amount_bucket"), "paid_on_time_rate": t("on_time_payment_rate")},
            ),
            width="stretch",
        )
    with col4:
        st.subheader(t("on_time_rate_by_due_gap_bucket"))
        due_gap_df = tables["due_gap_summary"].copy()
        st.plotly_chart(
            px.bar(
                due_gap_df,
                x="due_gap_bucket",
                y="paid_on_time_rate",
                labels={"due_gap_bucket": t("due_gap_bucket"), "paid_on_time_rate": t("on_time_payment_rate")},
            ),
            width="stretch",
        )

    col5, col6 = st.columns(2)
    with col5:
        st.subheader(t("reversal_delay"))
        reversal_delay_df = pd.DataFrame({"hours_until_reversal": summary["reversal_delay_hours"].dropna().astype(float)})
        st.plotly_chart(
            px.histogram(reversal_delay_df, x="hours_until_reversal", labels={"hours_until_reversal": t("hours_until_reversal")}),
            width="stretch",
        )
    with col6:
        st.subheader(t("reversal_rate_by_due_gap_bucket"))
        reversal_df = tables["reversal_summary"].copy()
        st.plotly_chart(
            px.bar(
                reversal_df,
                x="due_gap_bucket",
                y="reversal_rate",
                labels={"due_gap_bucket": t("due_gap_bucket"), "reversal_rate": t("reversal_rate")},
            ),
            width="stretch",
        )


def main() -> None:
    language = get_language()

    df = load_data()
    title_col, toggle_col = st.columns([0.85, 0.15])
    with title_col:
        st.title(get_text("page_title", language))
    with toggle_col:
        col_us, col_pt = st.columns(2)
        with col_us:
            if st.button("US", use_container_width=True, key="lang_us"):
                st.session_state["language"] = "US"
                st.rerun()
        with col_pt:
            if st.button("PT", use_container_width=True, key="lang_pt"):
                st.session_state["language"] = "PT"
                st.rerun()
    st.caption(get_text("page_caption", language))

    with st.sidebar:
        st.header(get_text("filters", language))
        month_options = sorted(pd.Series(pd.to_datetime(df["invoiceCreated"], format="mixed").dt.to_period("M").astype(str)).unique())
        selected_months = st.multiselect(get_text("invoice_creation_month", language), month_options, default=month_options)

    if selected_months:
        selected_mask = pd.to_datetime(df["invoiceCreated"], format="mixed").dt.to_period("M").astype(str).isin(selected_months)
        filtered_df = df.loc[selected_mask].copy()
    else:
        filtered_df = df.copy()

    all_registers = len(df)
    summary = build_invoice_summary(filtered_df)
    tables = build_summary_tables(summary)
    translated_tables = translate_tables(tables, language)
    activity = summarize_activity(filtered_df)
    model_coefs = build_payment_model(summary)

    render_metrics(all_registers, summary, activity, tables, model_coefs, language)

    with st.expander(get_text("monthly_summary", language)):
        st.dataframe(translated_tables["monthly"], width="stretch")

    render_charts(summary, activity, tables, language)

    st.subheader(get_text("factors_linked_to_on_time_payment", language))
    model_table = model_coefs.copy()
    model_table["feature"] = model_table["feature"].str.replace("num__", "", regex=False).str.replace("cat__", "", regex=False)
    model_table = model_table.rename(
        columns={
            "feature": get_text("feature", language),
            "coefficient": get_text("coefficient", language),
            "abs_coefficient": get_text("abs_coefficient", language),
        }
    )
    st.dataframe(model_table[[get_text("feature", language), get_text("coefficient", language), get_text("abs_coefficient", language)]], width="stretch")

    st.download_button(
        label=get_text("download_filtered_invoice_summary", language),
        data=summary.to_csv(index=False).encode("utf-8"),
        file_name=f"{get_text('download_filtered_invoice_filename', language)}.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
