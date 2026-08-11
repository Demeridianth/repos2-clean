from phoenix.evals import LLM
from phoenix.evals import create_classifier
from phoenix.client import Client
from phoenix.evals import evaluate_dataframe
from phoenix.trace import suppress_tracing
from phoenix.evals.utils import to_annotation_dataframe
import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
load_dotenv()

#  Basic completeness evaluation that checks whether the agent’s output completely answers the input.
#  If you hit Rate Limit Error = change model to gpt-4o-mini, set "max_retries" to 5 OR MORE

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
   - Generic statements like "both companies are good" do NOT satisfy this requirement
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


# LLM Judge
llm = LLM(model="gpt-4o-mini", provider="openai")  

# Evaluator
completeness_evaluator = create_classifier(
    name="completeness",
    prompt_template=financial_completeness_template,
    llm=llm,
    choices={"complete": 1.0, "incomplete": 0.0},
)


if __name__ == '__main__':
    px_client = Client()
    df = px_client.spans.get_spans_dataframe(project_name="crewai-tracing-quickstart")
    parent_spans = df[df["span_kind"] == "CHAIN"]

    with suppress_tracing():
        results_df = evaluate_dataframe(
            dataframe=parent_spans,
            evaluators=[completeness_evaluator],
            # concurrency=1,
    )
        
    evaluations = to_annotation_dataframe(
    dataframe=results_df
    )

    # Replace NaN and inf values with JSON-safe alternatives
    evaluations_clean = evaluations.replace({np.nan: None, np.inf: None, -np.inf: None})

    # Drop rows where label, score, and explanation are all None
    evaluations_clean = evaluations_clean.dropna(
        subset=["label", "score", "explanation"], how="all"
    )
    Client().spans.log_span_annotations_dataframe(
    dataframe=evaluations
)

