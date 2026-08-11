import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

os.environ["PHOENIX_API_KEY"] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJBcGlLZXk6MSJ9.3AcRijiMZxhe3qZE25kipsKj0C1SBfdaHY1EytqmWZk'
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = 'https://app.phoenix.arize.com/s/TUTORIAL_NEXUS'
os.environ["SERPER_API_KEY"] = 'e2920ba872029c9b8aadeae3aedb39ae116cfc26'
os.environ["OPENAI_API_KEY"] = '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'


# --- Phoenix ---
from phoenix.client import Client
from phoenix.evals import evaluate_dataframe
from phoenix.evals.utils import to_annotation_dataframe
from phoenix.trace import suppress_tracing

# --- Your evaluator (example using OpenAI) ---
from phoenix.evals import OpenAIModel, HallucinationEvaluator

# ------------------------------------------------------------------
# 1️⃣ Connect to Phoenix
# ------------------------------------------------------------------

client = Client()

PROJECT_NAME = "crewai-tracing-quickstart"  # 🔴 CHANGE THIS

# ------------------------------------------------------------------
# 2️⃣ Get ALL spans as a DataFrame
# ------------------------------------------------------------------

spans_df = client.spans.get_spans_dataframe(project_name=PROJECT_NAME)

print(f"Total spans pulled: {len(spans_df)}")

if spans_df.empty:
    raise ValueError("No spans found in project")

# ------------------------------------------------------------------
# 3️⃣ Filter only CHAIN spans with valid input/output
# ------------------------------------------------------------------

required_columns = [
    "span_id",
    "trace_id",
    "span_kind",
    "attributes.input.value",
    "attributes.output.value",
]

missing_cols = [c for c in required_columns if c not in spans_df.columns]
if missing_cols:
    raise ValueError(f"Missing expected columns: {missing_cols}")

chain_spans = spans_df[spans_df["span_kind"] == "CHAIN"].copy()

chain_spans = chain_spans.dropna(
    subset=["attributes.input.value", "attributes.output.value"]
)

print(f"Valid CHAIN spans to evaluate: {len(chain_spans)}")

if chain_spans.empty:
    raise ValueError("No valid spans to evaluate.")

# ------------------------------------------------------------------
# 4️⃣ Create evaluator
# ------------------------------------------------------------------

model = OpenAIModel(
    model="gpt-4o-mini",  # or whichever you use
    api_key=os.getenv("OPENAI_API_KEY"),
)

hallucination_evaluator = HallucinationEvaluator(model=model)

# ------------------------------------------------------------------
# 5️⃣ Run BULK evaluation on entire DataFrame
# ------------------------------------------------------------------

with suppress_tracing():
    results_df = evaluate_dataframe(
        dataframe=chain_spans,
        evaluators=[hallucination_evaluator],
    )

print("Evaluation complete")

# ------------------------------------------------------------------
# 6️⃣ Convert to annotation format
# ------------------------------------------------------------------

evaluations = to_annotation_dataframe(results_df)

# Clean NaN/inf values
evaluations_clean = evaluations.replace(
    {np.nan: None, np.inf: None, -np.inf: None}
)

print(f"Logging {len(evaluations_clean)} annotations...")

# ------------------------------------------------------------------
# 7️⃣ Log back to Phoenix
# ------------------------------------------------------------------

client.spans.log_span_annotations_dataframe(
    dataframe=evaluations_clean
)

print("✅ All traces evaluated and logged successfully!")
