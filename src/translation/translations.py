from __future__ import annotations

from typing import Any

DEFAULT_LANGUAGE = "US"

_TEXTS = {
    "US": {
        "page_title": "Pix Invoice Analytics",
        "page_caption": "Interactive analysis for payment conversion, late payments, and reversals",
        "filters": "Filters",
        "invoice_creation_month": "Invoice creation month",
        "unique_invoices": "Unique Invoices",
        "paid": "Paid",
        "paid_after_due_date": "Paid after due date",
        "reversed": "Reversed",
        "total_registers": "Total Registers",
        "median_reversal_delay": "Median reversal delay",
        "executive_summary": "Executive summary",
        "monthly_summary": "Monthly summary",
        "factors_linked_to_on_time_payment": "Factors linked to on-time payment",
        "download_filtered_invoice_summary": "Download filtered invoice summary",
        "download_filtered_invoice_filename": "filtered_invoice_summary",
        "activity_by_hour": "Activity by hour",
        "late_payment_rate_by_month": "Late payment rate by month",
        "on_time_rate_by_amount_bucket": "On-time rate by amount bucket",
        "on_time_rate_by_due_gap_bucket": "On-time rate by due-gap bucket",
        "reversal_delay": "Reversal delay",
        "reversal_rate_by_due_gap_bucket": "Reversal rate by due-gap bucket",
        "hour": "Hour",
        "log_events": "Log events",
        "month": "Month",
        "late_payment_rate_pct": "Late payment rate (%)",
        "amount_bucket": "Amount bucket",
        "on_time_payment_rate": "On-time payment rate",
        "due_gap_bucket": "Due-gap bucket",
        "hours_until_reversal": "Hours until reversal",
        "reversal_rate": "Reversal rate",
        "metric": "Metric",
        "value": "Value",
        "created_month": "Created month",
        "total_invoices": "Total invoices",
        "paid_count": "Paid count",
        "paid_late_count": "Paid late count",
        "paid_rate": "Paid rate",
        "late_rate": "Late rate",
        "invoice_count": "Invoice count",
        "feature": "Feature",
        "coefficient": "Coefficient",
        "abs_coefficient": "Absolute coefficient",
        "best_deployment_title": "Best deployment",
        "payment_conversion_title": "Payment conversion",
        "payment_drivers_title": "On-time payment drivers",
        "overdue_trend_title": "Overdue trend",
        "reversal_rate_title": "Reversal rate",
        "reversal_timing_title": "Reversal timing",
    },
    "PT": {
        "page_title": "Análise de Faturas Pix",
        "page_caption": "Análise interativa para conversão de pagamentos, pagamentos atrasados e reversões",
        "filters": "Filtros",
        "invoice_creation_month": "Mês de criação da fatura",
        "unique_invoices": "Faturas únicas",
        "paid": "Pagas",
        "paid_after_due_date": "Pagas após a data de vencimento",
        "reversed": "Revertidas",
        "total_registers": "Total de registros",
        "median_reversal_delay": "Atraso mediano de reversão",
        "executive_summary": "Resumo executivo",
        "monthly_summary": "Resumo mensal",
        "factors_linked_to_on_time_payment": "Fatores ligados ao pagamento no prazo",
        "download_filtered_invoice_summary": "Baixar resumo filtrado de faturas",
        "download_filtered_invoice_filename": "resumo_faturas_filtradas",
        "activity_by_hour": "Atividade por hora",
        "late_payment_rate_by_month": "Taxa de pagamentos atrasados por mês",
        "on_time_rate_by_amount_bucket": "Taxa de pagamento no prazo por faixa de valor",
        "on_time_rate_by_due_gap_bucket": "Taxa de pagamento no prazo por faixa de diferença para o vencimento",
        "reversal_delay": "Atraso de reversão",
        "reversal_rate_by_due_gap_bucket": "Taxa de reversão por faixa de diferença para o vencimento",
        "hour": "Hora",
        "log_events": "Eventos de log",
        "month": "Mês",
        "late_payment_rate_pct": "Taxa de pagamentos atrasados (%)",
        "amount_bucket": "Faixa de valor",
        "on_time_payment_rate": "Taxa de pagamento no prazo",
        "due_gap_bucket": "Faixa de diferença para o vencimento",
        "hours_until_reversal": "Horas até a reversão",
        "reversal_rate": "Taxa de reversão",
        "metric": "Métrica",
        "value": "Valor",
        "created_month": "Mês de criação",
        "total_invoices": "Total de faturas",
        "paid_count": "Pagas",
        "paid_late_count": "Atrasadas",
        "paid_rate": "Taxa de pagamento",
        "late_rate": "Taxa de atraso",
        "invoice_count": "Quantidade de faturas",
        "feature": "Recurso",
        "coefficient": "Coeficiente",
        "abs_coefficient": "Coeficiente absoluto",
        "best_deployment_title": "Melhor janela de implantação",
        "payment_conversion_title": "Conversão de pagamentos",
        "payment_drivers_title": "Fatores de pagamento no prazo",
        "overdue_trend_title": "Tendência de atraso",
        "reversal_rate_title": "Taxa de reversão",
        "reversal_timing_title": "Tempo de reversão",
    },
}


def normalize_language(language: str | None) -> str:
    if not language:
        return DEFAULT_LANGUAGE
    value = str(language).strip().upper()
    if value in {"EN", "US", "EN_US"}:
        return "US"
    if value in {"PT", "PT_BR", "PT_PT"}:
        return "PT"
    return DEFAULT_LANGUAGE


def get_text(key: str, language: str | None = None) -> str:
    lang = normalize_language(language)
    return _TEXTS[lang].get(key, key)


def get_language_label(language: str | None = None) -> str:
    lang = normalize_language(language)
    return "US" if lang == "US" else "PT"


def translate_executive_summary(items: list[dict[str, Any]], language: str | None = None) -> list[dict[str, str]]:
    lang = normalize_language(language)
    if lang != "PT":
        return items

    translated: list[dict[str, str]] = []
    for item in items:
        title = str(item.get("title", ""))
        value = str(item.get("value", ""))
        if title == "Best deployment":
            translated.append({"title": get_text("best_deployment_title", lang), "value": value.replace("Best deployment", "Melhor janela de implantação")})
        elif title == "Payment conversion":
            translated.append({"title": get_text("payment_conversion_title", lang), "value": value.replace("Payment conversion", "Conversão de pagamentos")})
        elif title == "On-time payment drivers":
            translated.append({"title": get_text("payment_drivers_title", lang), "value": value.replace("On-time payment drivers", "Fatores de pagamento no prazo")})
        elif title == "Overdue trend":
            translated.append({"title": get_text("overdue_trend_title", lang), "value": value.replace("Overdue trend", "Tendência de atraso")})
        elif title == "Reversal rate":
            translated.append({"title": get_text("reversal_rate_title", lang), "value": value.replace("Reversal rate", "Taxa de reversão")})
        elif title == "Reversal timing":
            translated.append({"title": get_text("reversal_timing_title", lang), "value": value.replace("Reversal timing", "Tempo de reversão")})
        else:
            translated.append({"title": title, "value": value})
    return translated


def translate_table_for_language(table: Any, language: str | None = None) -> Any:
    lang = normalize_language(language)
    if lang == "US":
        return table

    translated = table.copy()
    rename_map: dict[str, str] = {}
    if "created_month" in translated.columns:
        rename_map["created_month"] = get_text("created_month", lang)
    if "total_invoices" in translated.columns:
        rename_map["total_invoices"] = get_text("total_invoices", lang)
    if "paid" in translated.columns:
        rename_map["paid"] = get_text("paid_count", lang)
    if "paid_late" in translated.columns:
        rename_map["paid_late"] = get_text("paid_late_count", lang)
    if "paid_rate" in translated.columns:
        rename_map["paid_rate"] = get_text("paid_rate", lang)
    if "late_rate" in translated.columns:
        rename_map["late_rate"] = get_text("late_rate", lang)
    if "amount_bucket" in translated.columns:
        rename_map["amount_bucket"] = get_text("amount_bucket", lang)
    if "paid_on_time_rate" in translated.columns:
        rename_map["paid_on_time_rate"] = get_text("on_time_payment_rate", lang)
    if "invoice_count" in translated.columns:
        rename_map["invoice_count"] = get_text("invoice_count", lang)
    if "due_gap_bucket" in translated.columns:
        rename_map["due_gap_bucket"] = get_text("due_gap_bucket", lang)
    if "reversal_rate" in translated.columns:
        rename_map["reversal_rate"] = get_text("reversal_rate", lang)
    if "Metric" in translated.columns:
        rename_map["Metric"] = get_text("metric", lang)
    if "Value" in translated.columns:
        rename_map["Value"] = get_text("value", lang)
    if rename_map:
        translated = translated.rename(columns=rename_map)
    return translated
