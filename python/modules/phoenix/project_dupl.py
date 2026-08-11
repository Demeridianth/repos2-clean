# simple test crew
from crewai import Agent, Crew, Task, Process
from phoenix.otel import register
import os
from crewai_tools import SerperDevTool







tracer_provider = register(
    project_name="financial_tool_test",  # <-- THIS determines the Phoenix project
    auto_instrument=True
)

search_tool = SerperDevTool()



result = search_tool.run({"search_query": "AAPL financial analysis"})
print(result)  # Should print real search results from Serper

researcher = Agent(
    role="Financial Research Analyst",
    goal="Gather financial data for {{tickers}} and {{focus}}",
    backstory="You are a Senior Financial Research Analyst.",
    verbose=True,
    allow_delegation=False,
    max_iter=1,
    tools=[search_tool],
)

writer = Agent(
    role="Financial Report Writer",
    goal="Summarize research into actionable insights",
    backstory="Experienced financial content writer",
    verbose=True,
    allow_delegation=True,
    max_iter=1,
)

task1 = Task(
    description="Research: {{tickers}}, Focus: {{focus}}",
    expected_output="Detailed financial research summary",
    agent=researcher,
)

task2 = Task(
    description="Write a report based on the research above",
    expected_output="Polished financial report",
    agent=writer,
)

user_inputs = {"tickers": "AAPL", "focus": "financial analysis"}

crew = Crew(agents=[researcher, writer], tasks=[task1, task2], process=Process.sequential)
result = crew.kickoff(inputs=user_inputs)

result = search_tool.run({"search_query": "AAPL financial analysis"})
print(result)  # Should print real search results from Serper