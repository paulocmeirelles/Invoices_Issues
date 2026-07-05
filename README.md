# Pix Invoice Analysis Dashboard

This project analyzes a Pix Invoice lifecycle dataset and presents the findings through an interactive dashboard. It answers business questions about the best deployment window, payment conversion, overdue behavior, reversal rates, and the factors that influence payment and reversal outcomes.

## Challenge (English)

A Pix Invoice is one of the main methods for an enterprise to charge customers. Similarly to a boleto, an Invoice is first issued with an expected amount to be paid, and then customers pay it using their bank app by scanning a QR code or copying the payment information.

You will receive access to a random Invoice Log Dataset. Each Invoice can have several Logs, indicating each step of its lifecycle. Create a report using charts, tables, text, or other visualization tools to answer the following questions:

1. Deployment timing
   - When is the best time to deploy the Invoice application?
2. Payment conversion
   - What percentage of invoices are paid and what percentage are paid after the due date?
   - How has the overdue payment rate evolved over the available months?
   - Which factors influence whether an invoice is paid on time?
3. Reversals
   - What percentage of invoices are partially or totally reversed?
   - How long does it usually take for an invoice to be reversed?
   - Which factors influence whether an invoice is reversed and whether the reversal is partial or total?
4. Additional insight
   - Any other relevant insight you find useful.

## Desafio (Português)

Um Pix Invoice é um dos principais métodos usados por uma empresa para cobrar clientes. Assim como um boleto, um Invoice é emitido inicialmente com um valor esperado a ser pago, e depois os clientes realizam o pagamento pelo aplicativo do banco, escaneando o QR Code ou copiando as informações de pagamento.

Você receberá acesso a um dataset aleatório de logs de invoice. Cada invoice pode ter vários logs, indicando cada etapa do seu ciclo de vida. Crie um relatório, utilizando gráficos, tabelas, texto ou outras ferramentas de visualização, para responder às perguntas abaixo:

1. Momento de implantação
   - Quando é o melhor momento para implantar a aplicação de Invoice?
2. Conversão de pagamento
   - Qual percentual de invoices são pagos e qual percentual é pago após a data de vencimento?
   - Como evoluiu a taxa de pagamento em atraso ao longo dos meses disponíveis?
   - Quais fatores influenciam se a invoice será paga no prazo?
3. Reversões
   - Qual percentual de invoices são parcialmente ou totalmente revertidos?
   - Quanto tempo costuma levar para uma invoice ser revertida?
   - Quais fatores influenciam se uma invoice será revertida e se a reversão é parcial ou total?
4. Insight adicional
   - Qualquer outro insight relevante que você considerar útil.

## What this project includes

- Data loading and cleaning from the CSV file
- Invoice-level aggregation and lifecycle analysis
- Interactive charts and summary cards in a Streamlit dashboard
- Executive summary insights for deployment, conversion, overdue behavior, and reversals
- English/Portuguese language toggle

## Project structure

- app.py: interactive Streamlit dashboard
- main.py: entry point for running the analysis workflow
- src/invoice/processing.py: invoice data loading and aggregation
- src/analytics/analysis.py: analysis and executive summary calculations
- src/reports/visuals.py: chart and report generation
- src/translation/translations.py: English/Portuguese text helpers
- tests/: regression tests for the analysis logic

## Requirements

- Python 3.12
- pip
- Virtual environment

Install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## How to run (English)

From the project root:

```bash
source venv/bin/activate
streamlit run app.py --server.headless true --server.port 8501
```

Then open:

```text
http://localhost:8501
```

## Como executar (Português)

Na raiz do projeto:

```bash
source venv/bin/activate
streamlit run app.py --server.headless true --server.port 8501
```

Depois abra:

```text
http://localhost:8501
```

## Notes

- The dashboard reads the dataset file named InvoiceLog Dataset.csv.
- The app supports switching between English and Portuguese from the interface.
- Generated reports can be found in the report_outputs directory.
