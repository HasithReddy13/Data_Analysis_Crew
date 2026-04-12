from crewai import Agent, Task, Crew, LLM

llm = LLM(
    model="ollama/llama3.1:8b",
    base_url="http://localhost:11434"
)

researcher = Agent(
    role="Researcher",
    goal="Find useful information",
    backstory="You are a helpful research assistant.",
    llm=llm,
    verbose=True
)

task = Task(
    description="Summarize what agentic AI systems are in 3 bullet points.",
    expected_output="3 bullet points explaining agentic AI",
    agent=researcher
)

crew = Crew(agents=[researcher], tasks=[task], verbose=True)
result = crew.kickoff()
print(result)
