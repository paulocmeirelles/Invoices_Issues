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

## How the dataset works

The dataset contains one row per invoice event log. Each invoice can have multiple logs that represent its lifecycle stages, such as creation, payment, overdue status, and reversal.

In practice, the analysis works by:

- grouping the logs by invoice to reconstruct the full lifecycle of each invoice;
- identifying whether the invoice was paid, paid late, partially reversed, or fully reversed;
- using the timestamps in the logs to calculate metrics such as payment delay and reversal time;
- aggregating the results to produce business insights and visualizations.

This structure allows the dashboard to answer questions about deployment timing, payment conversion, overdue behavior, and reversal patterns.

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

## Como o dataset funciona

O dataset contém uma linha para cada log de evento da invoice. Cada invoice pode ter vários logs que representam as etapas do seu ciclo de vida, como criação, pagamento, status de atraso e reversão.

Na prática, a análise funciona assim:

- agrupando os logs por invoice para reconstruir todo o ciclo de vida de cada invoice;
- identificando se a invoice foi paga, paga com atraso, parcialmente revertida ou totalmente revertida;
- usando os timestamps dos logs para calcular métricas como atraso no pagamento e tempo de reversão;
- agregando os resultados para gerar insights de negócio e visualizações.

Essa estrutura permite que o dashboard responda perguntas sobre melhor momento de implantação, conversão de pagamento, comportamento de atraso e padrões de reversão.

## Estrutura do projeto

- app.py: dashboard interativo em Streamlit
- main.py: ponto de entrada para executar o fluxo de análise
- src/invoice/processing.py: carregamento e agregação dos dados das invoices
- src/analytics/analysis.py: cálculos de análise e resumo executivo
- src/reports/visuals.py: geração de gráficos e relatórios
- src/translation/translations.py: helpers de texto em inglês e português
- tests/: testes de regressão para a lógica de análise

## O que este projeto inclui

- Carregamento e limpeza dos dados a partir do arquivo CSV
- Agregação de dados no nível da invoice e análise do ciclo de vida
- Gráficos interativos e cards de resumo em um dashboard Streamlit
- Insights executivos sobre melhor momento de implantação, conversão, comportamento de atraso e reversões
- Alternância entre inglês e português na interface

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
