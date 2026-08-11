from phoenix.otel import register
from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool
from phoenix.client import Client
import os




tracer_provider = register(project_name="crewai-tracing-quickstart-tutorial", auto_instrument=True)



search_tool = SerperDevTool()

researcher = Agent(
    role="Financial Research Analyst",
    goal="Gather up-to-date financial data, trends, and news for the target companies or markets",
    backstory="""
        You are a Senior Financial Research Analyst.
    """,
    verbose=True,
    allow_delegation=False,
    max_iter=2,
    tools=[search_tool],
)

writer = Agent(
    role="Financial Report Writer",
    goal="Compile and summarize financial research into clear, actionable insights",
    backstory="""
        You are an experienced financial content writer.
    """,
    verbose=True,
    allow_delegation=True,
    max_iter=1
)


task1 = Task(
    description="""
        Research: {tickers}
        Focus on: {focus}
    """,
    expected_output="Detailed financial research summary with web search findings",
    agent=researcher,
)

task2 = Task(
    description="Write a report based on the research above.",
    expected_output="A polished financial analysis report",
    agent=writer,
)


crew = Crew(
    agents=[researcher, writer],
    tasks=[task1, task2],
    verbose=True,
    process=Process.sequential,
)

user_inputs = {
    "tickers": "TSLA",
    "focus": "financial analysis and market outlook"
}

result = crew.kickoff(inputs=user_inputs)
