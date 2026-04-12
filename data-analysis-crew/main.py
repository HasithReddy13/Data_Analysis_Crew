from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import FileReadTool, DirectoryReadTool
from tools.statistical_profiler import StatisticalProfilerTool

# using ollama so we don't need any paid API keys
# make sure ollama is running in another terminal before starting this
llm = LLM(
    model="ollama/llama3.1:8b",
    base_url="http://localhost:11434"
)

# ============ TOOLS ============

# our custom tool - this is the main one we built from scratch
profiler_tool = StatisticalProfilerTool()

# built-in crewai tools
file_read_tool = FileReadTool()
directory_read_tool = DirectoryReadTool(directory="data")

# ============ AGENTS ============

# this is the controller agent - it doesn't do analysis itself,
# it just takes what the other two agents produced and writes the final report
# had to set allow_delegation=False because the local model kept trying
# to pass the work back to other agents instead of writing the report
controller = Agent(
    role="Data Analysis Manager",
    goal="Write a final executive summary report by compiling findings from other agents.",
    backstory=(
        "You are a senior data analysis manager. Your job is to take the profiling results "
        "and analysis insights provided to you and write a polished executive summary report. "
        "You do NOT delegate. You write the report yourself using the context given to you. "
        "You always include specific numbers and statistics in your reports."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False
)

# agent that handles the data profiling step
# it has access to the profiler tool, file reader, and directory reader
data_engineer = Agent(
    role="Data Engineer",
    goal="Profile datasets using the Statistical Profiler tool and report findings.",
    backstory=(
        "You are an expert data engineer. When given a file path, you use the Statistical Profiler "
        "tool to analyze the dataset. After receiving the JSON results from the tool, you write "
        "a detailed human-readable summary of all the findings. You never make up numbers - "
        "you only report what the tools return."
    ),
    llm=llm,
    verbose=True,
    tools=[profiler_tool, file_read_tool, directory_read_tool],
    allow_delegation=False
)

# agent that interprets the profiling results and comes up with insights
# only has file read tool since it mainly works with the context passed from task 1
analyst = Agent(
    role="Data Analyst",
    goal="Interpret data profiles and generate business insights and recommendations.",
    backstory=(
        "You are a skilled data analyst. You receive data profiling results and interpret them. "
        "You identify trends, patterns, correlations, and anomalies. You reference specific "
        "numbers and statistics when making your points. "
        "You provide clear, actionable business recommendations backed by evidence from the data."
    ),
    llm=llm,
    verbose=True,
    tools=[file_read_tool],
    allow_delegation=False
)

# ============ TASKS ============

# step 1: profile the dataset
# the data engineer will use the profiler tool and then summarize what it found
# had to be very explicit about "do not invent numbers" because the local model
# tends to hallucinate statistics if you don't tell it not to
profiling_task = Task(
    description=(
        "First use the Directory Read tool to see what files are available in the data folder. "
        "Then use the Statistical Profiler tool with file_path='data/sales_data.csv' to profile the dataset. "
        "The tool will return a JSON with detailed statistics. Write a report covering:\n"
        "1. Dataset overview - number of rows and columns from the JSON output\n"
        "2. Data types for each column as shown in the JSON\n"
        "3. Missing values - list which columns have missing data with exact counts and percentages\n"
        "4. Numeric statistics - report the mean, median, std, min, max for each numeric column\n"
        "5. Categorical summaries - unique values and most common value per categorical column\n"
        "6. Correlations - list any strong correlations found\n"
        "7. Data quality score from the JSON\n\n"
        "Copy the actual numbers from the tool output into your report. Do not invent numbers."
    ),
    expected_output=(
        "A data profiling report with specific numbers from the tool output for all 7 sections."
    ),
    agent=data_engineer
)

# step 2: analyze the profiling results
# this task gets the output from task 1 automatically through the context parameter
# the analyst reads through what the data engineer found and pulls out business insights
analysis_task = Task(
    description=(
        "You have been given a data profiling report with specific statistics. "
        "Use the File Read tool to read 'data/sales_data.csv' and examine a few rows if needed.\n\n"
        "Then write an analysis covering:\n"
        "1. Key trends and patterns in the sales data based on the profiling numbers\n"
        "2. What the correlations or lack of correlations mean for the business\n"
        "3. Data quality issues - which columns have missing data and recommended fixes\n"
        "4. Three specific business recommendations backed by numbers from the data\n\n"
        "Use actual statistics from the profiling report in your analysis."
    ),
    expected_output=(
        "An analysis report with trends, correlation insights, data quality issues, "
        "and 3 recommendations referencing actual data numbers."
    ),
    agent=analyst,
    context=[profiling_task]  # gets task 1 output automatically
)

# step 3: write the final report
# the controller gets context from BOTH previous tasks and compiles everything
# output_file saves the report to disk so we have a deliverable
report_task = Task(
    description=(
        "Compile the profiling report and analysis into a final executive summary with:\n"
        "1. Executive Summary - 2-3 sentences with the key takeaway\n"
        "2. Data Overview and Quality Assessment - rows, columns, quality score, missing values\n"
        "3. Key Findings and Insights - main trends with specific numbers\n"
        "4. Recommendations - top 3 actionable recommendations\n"
        "5. Next Steps - immediate actions to take\n\n"
        "Use the specific numbers from the previous reports. Do not use any tools."
    ),
    expected_output=(
        "A complete executive summary with all 5 sections including specific statistics."
    ),
    agent=controller,
    context=[profiling_task, analysis_task],  # gets both task 1 and task 2 outputs
    output_file="outputs/final_report.md"
)

# ============ CREW ============

# putting it all together
# sequential process means tasks run one after another (1 -> 2 -> 3)
# memory is off because crewai's memory system needs OpenAI by default
# and we're running everything locally with ollama
crew = Crew(
    agents=[controller, data_engineer, analyst],
    tasks=[profiling_task, analysis_task, report_task],
    process=Process.sequential,
    verbose=True,
    memory=False
)

# entry point
if __name__ == "__main__":
    print("Starting Data Analysis Crew...")
    print("=" * 50)
    result = crew.kickoff()
    print("\n" + "=" * 50)
    print("FINAL REPORT:")
    print("=" * 50)
    print(result)
