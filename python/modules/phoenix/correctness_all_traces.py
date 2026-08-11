import numpy as np
import pandas as pd
from phoenix.evals import LLM, create_classifier, evaluate_dataframe
from phoenix.evals.utils import to_annotation_dataframe
from phoenix.client import Client
from phoenix.trace import suppress_tracing
from dotenv import load_dotenv
import os

# load_dotenv()

# PHOENIX_KEY = os.getenv('PHOENIX_API_KEY')
# PHOENIX_ENDPOINT = os.getenv('PHOENIX_COLLECTOR_ENDPOINT')
# SERPER_KEY = os.getenv('SERPER_API_KEY')
# OPENAI_KEY = os.getenv('OPENAI_API_KEY')

os.environ["PHOENIX_API_KEY"] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJBcGlLZXk6MSJ9.3AcRijiMZxhe3qZE25kipsKj0C1SBfdaHY1EytqmWZk'
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = 'https://app.phoenix.arize.com/s/TUTORIAL_NEXUS'
os.environ["SERPER_API_KEY"] = 'e2920ba872029c9b8aadeae3aedb39ae116cfc26'
os.environ["OPENAI_API_KEY"] = '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'


# -----------------------------
# 1️⃣ Setup your LLM evaluator
# -----------------------------
financial_completeness_template = """
You are evaluating whether a financial research report correctly completes ALL parts of the user's task with COMPREHENSIVE coverage.

User input: {attributes.input.value}

Generated report: {attributes.output.value}

To be marked as "complete", the report MUST meet ALL of these strict requirements:

1. TICKER COVERAGE (MANDATORY):
   - Cover ALL companies/tickers mentioned in the input
   - If multiple tickers are listed, EACH must have dedicated analysis (not just mentioned in passing)
   - For multiple tickers, the report must provide COMPARATIVE analysis when relevant

2. FOCUS AREA COVERAGE (MANDATORY):
   - Address ALL focus areas mentioned in the input
   - If the focus mentions multiple topics (e.g., "earnings and outlook"), BOTH must be thoroughly addressed
   - Each focus area must have substantial content, not just a brief mention

3. FINANCIAL DATA REQUIREMENTS (MANDATORY):
   - For EACH ticker, the report must include:
     * Current/recent stock price or performance data
     * At least 2 key financial ratios (P/E, P/B, debt-to-equity, ROE, etc.)
     * Revenue or earnings information
     * Recent news or developments (within last 6 months)
   - If focus mentions specific metrics (e.g., "P/E ratio"), those MUST be explicitly provided

4. DEPTH REQUIREMENT (MANDATORY):
   - Each ticker must have at least 3-4 sentences of dedicated analysis
   - Generic statements without specific data do NOT count
   - The report must demonstrate thorough research, not superficial coverage

5. COMPARISON REQUIREMENT (if multiple tickers):
   - If 2+ tickers are requested, the report MUST include direct comparisons
   - Comparisons should cover multiple key metrics side-by-side
   - Generic statements like "both companies are good" DO NOT satisfy this requirement
   - Must explicitly state which company performs better/worse on specific metrics

The report is "incomplete" if it fails ANY of the above requirements, including:
- Missing any ticker or only mentioning it briefly
- Failing to address any focus area or only addressing it superficially
- Missing required financial data for any ticker
- Providing generic analysis without specific metrics or data
- Failing to provide comparisons when multiple tickers are requested
- Not meeting the depth requirement for any ticker

Respond with ONLY one word: "complete" or "incomplete"
Then provide a detailed explanation of which specific requirements were met or failed.
"""

llm = LLM(model="gpt-4o", provider="openai")
completeness_evaluator = create_classifier(
    name="completeness",
    prompt_template=financial_completeness_template,
    llm=llm,
    choices={"complete": 1.0, "incomplete": 0.0},
)

# -----------------------------
# 3️⃣ Connect to Phoenix client and fetch spans
# -----------------------------
px_client = Client()
df = px_client.spans.get_spans_dataframe(project_name="crewai-tracing-quickstart")
print(f"Total spans fetched: {len(df)}")
print(f"Unique CHAIN spans: {len(df[df['span_kind'] == 'CHAIN'])}")

# -----------------------------
# 4️⃣ Loop over each CHAIN span
# -----------------------------
chain_spans = df[df["span_kind"] == "CHAIN"]

for idx, span_row in chain_spans.iterrows():
    span_id = span_row["span_id"]

    # Skip spans without input/output
    if pd.isna(span_row.get("attributes.input.value")) or pd.isna(span_row.get("attributes.output.value")):
        print(f"Skipping span {span_id} (missing input/output)")
        continue

    # Make a dataframe for a single span
    single_span_df = pd.DataFrame([span_row])

    print(f"Evaluating span {span_id}...")

    # Evaluate
    with suppress_tracing():
        results_df = evaluate_dataframe(
            dataframe=single_span_df,
            evaluators=[completeness_evaluator]
        )

    # Convert to Phoenix annotation dataframe
    evaluations = to_annotation_dataframe(results_df)

    # Clean dataframe for JSON logging
    evaluations_clean = evaluations.replace({np.nan: None, np.inf: None, -np.inf: None})
    evaluations_clean = evaluations_clean.dropna(subset=["label", "score", "explanation"], how="all")

    if evaluations_clean.empty:
        print(f"No valid evaluation results for span {span_id}, skipping logging.")
        continue

    # Log back to Phoenix
    px_client.spans.log_span_annotations_dataframe(dataframe=evaluations_clean)
    print(f"Logged {len(evaluations_clean)} annotations for span {span_id}")

print("✅ All CHAIN spans evaluated and logged successfully.")