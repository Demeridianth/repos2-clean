import os
from phoenix.otel import register
from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
load_dotenv()


tracer_provider = register(project_name="crewai-tracing-quickstart", auto_instrument=True) # to which project


test_queries = [
    {"tickers": "AAPL", "focus": "financial analysis and market outlook"},
    {"tickers": "NVDA", "focus": "valuation metrics and growth prospects"},
    {"tickers": "AMZN", "focus": "profitability and market share"},
    {"tickers": "AAPL, MSFT", "focus": "comparative financial analysis"},
    {"tickers": "META, SNAP, PINS", "focus": "social media sector trends"},
    {"tickers": "RIVN", "focus": "financial health and viability"},
    {"tickers": "SNOW", "focus": "revenue growth trajectory"},
    {"tickers": "KO", "focus": "dividend yield and stability"},
    {"tickers": "META", "focus": "latest developments and stock performance"},
    {"tickers": "AAPL, MSFT, GOOGL, AMZN, META", "focus": "big tech comparison and market outlook"},
    {"tickers": "AMC", "focus": "financial analysis and market sentiment"},
]

for query in test_queries:
    search_tool = SerperDevTool()
    
    researcher = Agent(
        role="Financial Research Analyst",
        goal="Gather up-to-date financial data, trends, and news for the target companies or markets",
        backstory="""
            You are a Senior Financial Research Analyst.
        """,
        verbose=True,
        allow_delegation=False,
        max_iter=1,
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
            Research: {{tickers}}
            Focus on: {{focus}}
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
        verbose=1,
        process=Process.sequential,
    )
    crew.kickoff(inputs=query)

    

