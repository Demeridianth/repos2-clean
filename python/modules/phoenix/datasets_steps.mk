# filter the incomplete ones
evals['completeness'].label == 'incomplete'
# check all the boxes

Current Task:
Research: {tickers}
Focus on: {focus}

# add to existing datasets or creat a new one

# saving a prompt:

#     Navigate to your project in Phoenix.
#     Open the Traces view and click into a trace.
#     Find a span that contains a prompt.
#     Save the prompt to the Prompt Hub.

# what is a tool (like Serper)
Think of the model as a smart assistant. By default, it can only use its internal knowledge, which is limited and static (it doesn’t know events or stock prices from yesterday, for example). A tool lets it:

Get real-time or external data
Example: “Search the web for latest news about AMC stock.”
Tool: search_the_internet_with_serper

Perform calculations
Example: “Calculate ROI based on these inputs.”
Tool: could be a Python function or math executor

Interact with APIs
Example: “Fetch latest sales data from Salesforce”
Tool: REST API connector

Manipulate files or databases
Example: “Write these results to a CSV” or “Query this database”


# ERRORS
 
# IF
"tries exhausted"" = change to gpt-mini

# IF
(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.UniqueViolationError'>: duplicate key value violates unique constraint "uq_traces_trace_id" DETAIL: Key (trace_id)=(709f92b83e4162f2d26e9fc8b2f3b218) already exists. [SQL: INSERT INTO phoenix.traces (project_rowid, trace_id, project_session_rowid, start_time, end_time) VALUES ($1::INTEGER, $2::VARCHAR, $3::INTEGER, $4::TIMESTAMP WITH TIME ZONE, $5::TIMESTAMP WITH TIME ZONE) RETURNING phoenix.traces.id] [parameters: (28, '709f92b83e4162f2d26e9fc8b2f3b218', None, datetime.datetime(2026, 2, 27, 11, 11, 55, 923637, tzinfo=datetime.timezone.utc), datetime.datetime(2026, 2, 27, 11, 11, 59, 110292, tzinfo=datetime.timezone.utc))] (Background on this error at: https://sqlalche.me/e/20/gkpj)

=

remove tools from ui playground



