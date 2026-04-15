Technical Report
Data Analysis Crew — Multi-Agent Agentic AI System
Author: Hasith Reddy Rapolu
Course: Big Data Architecture and Management
University: Northeastern University
Date: April 2026
Platform: CrewAI with Ollama (LLaMA 3.1 8B)
Domain: Data Analysis
 

1. Introduction
1.1 Project Overview
This project implements a multi-agent agentic AI system designed to automate the data analysis pipeline. The system uses three specialized AI agents, a Controller (Data Analysis Manager), a Data Engineer, and a Data Analyst, orchestrated through CrewAI in a sequential workflow. Each agent has a defined role, specific tools, and clear objectives, working collaboratively to profile a dataset, extract insights, and generate a comprehensive executive report.
1.2 Objectives
•	Design and implement a controller agent that orchestrates task delegation across specialized agents
•	Integrate both pre-built and custom tools into the agentic workflow
•	Build a custom Statistical Profiler tool that extends system capabilities
•	Demonstrate sequential multi-agent collaboration with context passing
•	Evaluate system performance through defined metrics and test cases
1.3 Technology Stack
Component	Technology
Orchestration Framework	CrewAI 1.14.1
Language Model	LLaMA 3.1 8B (via Ollama)
Programming Language	Python 3.12
Data Processing	Pandas 2.0+, NumPy 1.24+
LLM Interface	LiteLLM
Execution	Local machine (no cloud API required)
 
2. System Architecture
2.1 Architecture Diagram
 
2.2 Architecture Description
The system follows a sequential orchestration pattern implemented through CrewAI's Process.sequential mode. Each task is assigned to a specific agent, and the output of earlier tasks is passed as context to later tasks.
Data Flow:
1.	User provides a CSV file path as input
2.	Task 1 (Profiling) is assigned to the Data Engineer, who uses the Statistical Profiler tool
3.	Task 2 (Analysis) receives the profiling output as context and is assigned to the Data Analyst
4.	Task 3 (Report) receives both profiling and analysis outputs, and the Controller writes the final report
5.	The final report is saved to outputs/final_report.md
2.3 Design Decisions
Decision	Rationale
Sequential over parallel execution	Tasks have dependencies, analysis requires profiling output, report requires both
Delegation disabled on all agents	The local LLM (8B parameters) performed better with explicit task assignment than with autonomous delegation
Memory disabled	CrewAI's memory system defaults to OpenAI embeddings; disabled to avoid API key dependency
Ollama for LLM	Provides free, local inference without cloud API costs or rate limits
 
3. Agent Design
3.1 Controller Agent - Data Analysis Manager
Attribute	Value
Role	Data Analysis Manager
Goal	Write a final executive summary report by compiling findings from other agents
Delegation	Disabled
Tools	None
Behavior: The controller receives context from both the profiling and analysis tasks. It synthesizes these inputs into a structured five-section executive report. By disabling delegation, we ensure the controller writes the report itself rather than attempting to re-delegate to other agents.
Prompting Strategy: The backstory explicitly instructs the agent to "write the report yourself using the context given to you" and "do NOT delegate." This was necessary because the local LLM initially attempted to output JSON tool-call objects instead of writing prose.
3.2 Data Engineer Agent
Attribute	Value
Role	Data Engineer
Goal	Profile datasets using tools and report findings with specific numbers
Delegation	Disabled
Tools	StatisticalProfilerTool (custom), FileReadTool, DirectoryReadTool
Behavior: The Data Engineer first uses the DirectoryReadTool to discover available files, then applies the StatisticalProfilerTool to generate a comprehensive JSON profile. It then translates the JSON output into a human-readable summary.
Prompting Strategy: The task description explicitly tells the agent to "copy the actual numbers from the tool output" and "do not invent numbers" to reduce hallucination.
3.3 Data Analyst Agent
Attribute	Value
Role	Data Analyst
Goal	Interpret data profiles and generate business insights and recommendations
Delegation	Disabled
Tools	FileReadTool
Behavior: Receives the profiling report as context and interprets the statistics to identify trends, patterns, and anomalies. Generates three actionable business recommendations backed by data evidence.
Prompting Strategy: The backstory emphasizes referencing "specific numbers" when making points, which helps ground the analysis in actual data rather than generic statements.
 
4. Tool Integration
4.1 Custom Tool: Statistical Profiler
Purpose: Automates comprehensive dataset profiling, replacing what would typically require multiple manual pandas operations.
Implementation:
class StatisticalProfilerTool(BaseTool):
    name: str = "Statistical Profiler"
    description: str = "Analyzes a CSV dataset and returns a comprehensive statistical profile..."
    args_schema: Type[BaseModel] = StatisticalProfilerInput
Input: file_path (string) — path to a CSV file
Output: JSON object containing:
Section	Fields
Overview	rows, columns, column_names, memory_usage_mb
Data Types	dtype per column
Missing Values	count and percentage per column
Numeric Stats	mean, median, std, min, max, skewness, outlier count
Categorical Stats	unique_values, top_value, top_frequency
Correlations	pairs with |r| > 0.7
Quality Score	weighted score (70% completeness + 30% uniqueness)
Error Handling:
•	FileNotFoundError — returns descriptive error message
•	Generic exceptions — caught and returned as error strings
•	Empty DataFrames — handled with conditional checks
•	Missing columns — handled with dtype-based filtering
Design Choices:
•	Outlier detection uses the 3-sigma rule (values beyond 3 standard deviations)
•	Correlation threshold set at 0.7 to capture only strong relationships
•	Quality score weights completeness (70%) higher than uniqueness (30%) as missing data has greater impact on analysis reliability
4.2 Built-in Tool: FileReadTool
Purpose: Reads the contents of any file, allowing agents to inspect raw data or configuration files.
Usage in System:
•	Data Engineer uses it to verify raw CSV content after profiling
•	Data Analyst uses it to examine specific data rows for deeper analysis
4.3 Built-in Tool: DirectoryReadTool
Purpose: Lists all files in a specified directory, enabling agents to discover available datasets.
Configuration: Initialized with directory="data" to scope it to the data folder.
Usage in System: Data Engineer uses it as the first step to identify which files are available before profiling.
 
5. Orchestration Design
5.1 Workflow
The crew executes three tasks sequentially:
Task 1: Data Profiling
  Agent: Data Engineer
  Tools: DirectoryReadTool → StatisticalProfilerTool → FileReadTool
  Output: Detailed profiling report with statistics
        │
        ▼ (context passed)

Task 2: Data Analysis
  Agent: Data Analyst
  Tools: FileReadTool
  Input Context: Profiling report from Task 1
  Output: Analysis with trends, insights, and recommendations
        │
        ▼ (context passed)

Task 3: Executive Report
  Agent: Data Analysis Manager
  Tools: None
  Input Context: Profiling report (Task 1) + Analysis (Task 2)
  Output: Final executive summary saved to outputs/final_report.md
5.2 Context Passing
CrewAI's context parameter enables output from earlier tasks to be injected into later tasks:
analysis_task = Task(
    ...
    context=[profiling_task]  # Receives Task 1 output
)

report_task = Task(
    ...
    context=[profiling_task, analysis_task]  # Receives Task 1 + Task 2 outputs
)
This ensures each agent has the information it needs without re-running tools.

5.3 Error Handling and Fallbacks
Scenario	Handling
File not found	StatisticalProfilerTool returns descriptive error message
Invalid CSV format	Pandas exception caught and returned as error string
LLM produces tool-call JSON instead of prose	Explicit backstory instructions to "write the report yourself"
Memory save failures	Memory disabled entirely to avoid OpenAI dependency errors
Tool validation errors	CrewAI's built-in retry mechanism attempts the tool call again
 
6. Challenges and Solutions
Challenge 1: CrewAI Version Compatibility
Problem: The initial Python 3.9 environment installed CrewAI 0.5.0, which lacked support for modern LLM providers and had incompatible dependencies.
Solution: Upgraded to Python 3.12 and recreated the virtual environment, which installed CrewAI 1.14.1 with full Ollama support.
Challenge 2: Gemini API Quota Issues
Problem: The Google Gemini free tier API returned "quota exceeded" errors with limit: 0, suggesting the free tier was not available for the account or region.
Solution: Switched to Ollama with LLaMA 3.1 8B running locally, eliminating all API dependencies and costs.
Challenge 3: Agent Delegation Loops
Problem: When allow_delegation=True, the controller agent attempted to delegate tasks back to other agents using JSON tool-call syntax instead of writing the report itself. This is a known behavior with smaller language models.
Solution: Set allow_delegation=False on all agents and added explicit instructions in backstory and task descriptions telling agents to complete tasks themselves.
Challenge 4: Memory System Requiring OpenAI
Problem: CrewAI's memory system defaults to OpenAI's GPT-4o-mini for memory analysis, causing errors when no OpenAI API key is set.
Solution: Disabled memory entirely with memory=False on the Crew object. Context passing between tasks was used instead to share information between agents.
Challenge 5: LLM Hallucinating Statistics
Problem: The local LLaMA 3.1 8B model sometimes generated fabricated statistics instead of using the actual numbers returned by the Statistical Profiler tool.
Solution: Added explicit prompting instructions such as "copy the actual numbers from the tool output" and "do not invent numbers." While this improved accuracy, it remains a known limitation of smaller models.
 
7. Evaluation - Test Cases and Results
7.1 Custom Tool Tests
ID	Test Case	Input	Expected Result	Actual Result	Status
T-01	Profile valid CSV file	data/sales_data.csv	JSON with 500 rows, 7 columns	Returned 500 rows, 7 columns	 Pass
T-02	Profile non-existent file	data/fake_file.csv	Error message returned	"Error: File not found."	 Pass
T-03	Detect missing values	data/sales_data.csv	Identify revenue and customer_rating gaps	revenue: 17 (3.4%), customer_rating: 29 (5.8%)	 Pass
T-04	Calculate numeric statistics	data/sales_data.csv	Mean, median, std, min, max per column	All values computed correctly	 Pass
T-05	Identify correlations	data/sales_data.csv	Report strong correlations (|r| > 0.7)	Correctly returned empty list	 Pass
T-06	Compute data quality score	data/sales_data.csv	Score between 0-100	Returned 99.1	 Pass
T-07	Handle empty CSV	Empty file with headers	Valid JSON with 0 rows	Returned overview with 0 rows	 Pass
T-08	Handle all-null column	CSV with entirely null column	100% missing for that column	Correctly reported 100%	 Pass
T-09	Categorical profiling	data/sales_data.csv	Unique values and top value	product: 4 unique, top "Gadget Y" (148)	 Pass
T-10	Outlier detection	data/sales_data.csv	Count values beyond 3 std deviations	Correctly returned 0 outliers	 Pass

Custom Tool Pass Rate: 10/10 (100%)
7.2 Agent Behavior Tests
ID	Test Case	Expected Behavior	Actual Behavior	Status
A-01	Data Engineer calls profiler tool	Invokes tool with correct file path	Tool called with 'data/sales_data.csv'	 Pass
A-02	Data Engineer uses DirectoryReadTool	Lists files before profiling	Directory contents listed	 Pass
A-03	Data Engineer writes summary	Human-readable report with numbers	Report generated	 Pass
A-04	Data Analyst receives context	Analysis references profiling data	Context passed successfully	 Pass
A-05	Data Analyst provides 3 recommendations	Three distinct recommendations	Three recommendations generated	 Pass
A-06	Controller writes all 5 sections	All report sections present	All 5 sections present	 Pass
A-07	Controller does not delegate	No delegation attempts	No delegation occurred	 Pass
A-08	Report saved to file	outputs/final_report.md created	File saved successfully	 Pass
A-09	Agents use actual numbers from tools	Statistics match tool output	LLM sometimes substituted numbers	Partial
A-10	System completes without errors	No crashes or exceptions	Completed successfully	 Pass
Agent Behavior Pass Rate: 9/10 (90%), 1 Partial
7.3 End-to-End System Tests
ID	Test Case	Description	Result	Status
E-01	Full pipeline execution	Run main.py start to finish	All 3 tasks completed	 Pass
E-02	Sequential context passing	Task outputs flow correctly	Context passed correctly	 Pass
E-03	Output file generation	Report saved to outputs/	File created with content	 Pass
E-04	Multiple consecutive runs	Run system 3 times	All runs succeeded	 Pass
E-05	Different dataset	New dataset with different structure	System adapts correctly	 Pass
End-to-End Pass Rate: 5/5 (100%)
 
8. Performance Metrics
8.1 Execution Time
Run	Task 1 (Profiling)	Task 2 (Analysis)	Task 3 (Report)	Total
1	45s	30s	35s	1m 50s
2	50s	25s	40s	1m 55s
3	40s	35s	30s	1m 45s
4	55s	30s	35s	2m 00s
5	45s	28s	38s	1m 51s
Average	47s	29.6s	35.6s	1m 52s
8.2 Tool Usage Metrics
Metric	Value
Average tool calls per run	3-5
Tool success rate	100%
Cache hit rate	~40%
Average tool execution time	< 1 second
8.3 Output Quality Metrics
Metric	Score	Notes
Report Completeness	100%	All 5 sections always generated
Report Structure	95%	Consistent formatting across runs
Statistical Accuracy	60-70%	LLM sometimes hallucinated numbers
Recommendation Relevance	75%	Generally reasonable but sometimes generic
Professional Tone	85%	Reports are well-written and structured
8.4 Reliability Metrics
Metric	Value
Task Completion Rate	100%
Crash Rate	0%
Error Recovery Rate	100%
Consistent Output Structure	95%
 
9. Accuracy Analysis
9.1 Component-Level Accuracy
Component	Accuracy	Explanation
Statistical Profiler Tool	100%	Pandas computations are deterministic
DirectoryReadTool	100%	File listing is deterministic
FileReadTool	100%	File reading is deterministic
Data Engineer Interpretation	~70%	Sometimes misquotes tool output
Data Analyst Insights	~65%	May fabricate unsupported trends
Controller Final Report	~60%	Compounds errors from previous agents
9.2 Root Cause of Accuracy Gaps
The accuracy degradation occurs at the LLM interpretation layer, not the tool layer. The LLaMA 3.1 8B model has limited ability to:
1.	Extract exact numbers from long JSON outputs — The model sometimes paraphrases numbers instead of copying them
2.	Distinguish between tool output and its own knowledge — The model occasionally substitutes fabricated statistics
3.	Maintain numerical precision across context passing — Numbers can drift between tasks
9.3 Accuracy Improvement Strategies Tested
Strategy	Impact
Adding "do not invent numbers" to prompts	Moderate improvement (~10%)
Adding "copy actual numbers from tool output"	Moderate improvement (~10%)
Disabling delegation	Eliminated JSON tool-call outputs
Explicit section requirements in tasks	Improved structure consistency
 
10. Agent Behavior Analysis
10.1 Data Engineer Agent
Strengths:
•	Consistently calls the StatisticalProfilerTool with correct parameters
•	Handles tool errors gracefully
•	Produces structured output that other agents can consume
Weaknesses:
•	Sometimes calls the profiler tool twice (redundant)
•	May not fully report all sections from the JSON output
•	Occasionally adds interpretations not directly from the data
10.2 Data Analyst Agent
Strengths:
•	Generates relevant business recommendations
•	Maintains professional analytical tone
•	Successfully uses context from Task 1
Weaknesses:
•	Recommendations can be generic rather than data-specific
•	Sometimes fabricates trends not supported by profiling data
•	Limited analysis depth due to model size constraints
10.3 Data Analysis Manager (Controller)
Strengths:
•	Consistently produces all 5 required report sections
•	Maintains professional executive summary format
•	Successfully synthesizes inputs from both previous tasks
Weaknesses:
•	With delegation enabled, attempts to re-delegate instead of writing
•	May not preserve exact statistics from earlier reports
•	Report depth limited by input quality from other agents
 
11. Limitations
11.1 System-Level Limitations
1.	Single-pass execution — No review or correction cycle between agents
2.	Sequential only — Cannot parallelize independent tasks
3.	No persistent memory — System does not learn from previous runs
4.	CSV-only input — Does not support other data formats
11.2 Model-Level Limitations
1.	Numerical hallucination — 8B model struggles to faithfully reproduce tool outputs
2.	Limited reasoning depth — Analysis and recommendations lack nuance
3.	Context window constraints — Very large datasets could exceed model limits
4.	No multi-modal support — Cannot generate charts or visualizations
11.3 Tool-Level Limitations
1.	No web search — Cannot fetch external benchmarks or industry context
2.	No semantic search — CSV search tools require API keys not available
3.	Static profiling — Does not support time-series or trend detection over time
4.	No data transformation — Profiler is read-only; cannot clean or modify data
 
12. Future Improvements
Priority	Improvement	Expected Impact
High	Upgrade to larger LLM (70B or cloud)	25-30% accuracy improvement
High	Add verification agent to review outputs	Catch and correct hallucinated numbers
Medium	Implement feedback loop between agents	Iterative improvement of report quality
Medium	Add visualization agent	Auto-generate charts for the report
Medium	Support multiple file formats	Broader real-world applicability
Low	Add web search tool	Industry context and benchmarking
Low	Build interactive web UI	Accessibility for non-technical users
Low	Implement parallel task execution	Faster processing time






 
13. Conclusion
The Data Analysis Crew system successfully demonstrates multi-agent orchestration for automated data analysis. The system achieves a 100% task completion rate and 100% tool reliability, producing structured executive reports consistently across all test runs.
The primary area for improvement is statistical accuracy (currently 60-70%), which is bounded by the local LLM's capability rather than the system architecture. The custom Statistical Profiler tool achieves 100% accuracy, confirming that the agentic framework and tool integration are sound.
Key takeaways:
•	Agent design matters — Clear role definitions and explicit prompting significantly improve agent behavior
•	Tool quality is critical — Well-designed tools with proper error handling are the foundation of reliable agentic systems
•	Model capability affects output — The gap between tool accuracy (100%) and final report accuracy (~60-70%) demonstrates that agentic system performance is bounded by the underlying LLM
•	Local LLMs are viable — While less accurate than cloud models, Ollama provides a cost-free, privacy-preserving alternative suitable for development and education
 
14. Appendices
Appendix A: File Listing
File	Description
main.py	Entry point — agents, tasks, and crew configuration
tools/statistical_profiler.py	Custom Statistical Profiler tool
tools/__init__.py	Package initializer
data/create_sample.py	Sample sales dataset generator
data/sales_data.csv	Sample dataset (500 rows, 7 columns)
outputs/final_report.md	Generated executive summary
requirements.txt	Python dependencies
README.md	Project documentation
Appendix B: Sample Statistical Profiler Output
{
  "overview": {
    "rows": 500,
    "columns": 7,
    "column_names": [
      "date", "product", "region",
      "units_sold", "revenue",
      "customer_rating", "return_rate"
    ],
    "memory_usage_mb": 0.04
  },
  "data_types": {
    "date": "object",
    "product": "object",
    "region": "object",
    "units_sold": "int64",
    "revenue": "float64",
    "customer_rating": "float64",
    "return_rate": "float64"
  },
  "missing_values": {
    "revenue": {"count": 17, "percentage": 3.4},
    "customer_rating": {"count": 29, "percentage": 5.8}
  },
  "numeric_stats": {
    "units_sold": {
      "mean": 246.88, "median": 248.0,
      "std": 142.66, "min": 10.0, "max": 497.0,
      "skewness": 0.01, "outliers": 0
    },
    "revenue": {
      "mean": 5118.39, "median": 5291.46,
      "std": 2918.77, "min": 145.86, "max": 9979.55,
      "skewness": -0.05, "outliers": 0
    },
    "customer_rating": {
      "mean": 3.0, "median": 3.0,
      "std": 1.16, "min": 1.0, "max": 5.0,
      "skewness": -0.0, "outliers": 0
    },
    "return_rate": {
      "mean": 0.15, "median": 0.16,
      "std": 0.09, "min": 0.0, "max": 0.3,
      "skewness": -0.09, "outliers": 0
    }
  },
  "categorical_stats": {
    "product": {
      "unique_values": 4,
      "top_value": "Gadget Y",
      "top_frequency": 148
    },
    "region": {
      "unique_values": 4,
      "top_value": "North",
      "top_frequency": 136
    }
  },
  "correlations": {
    "strong_correlations": []
  },
  "data_quality_score": 99.1
}
Appendix C: Sample Generated Report
Executive Summary
=================

1. Executive Summary
The data profiling report reveals a comprehensive insight into the sales
dataset with 500 rows and 7 columns. Data quality score is 99.1 with
minor missing values in revenue (3.4%) and customer_rating (5.8%).

2. Data Overview and Quality Assessment
- Rows: 500, Columns: 7
- Quality Score: 99.1/100
- Missing Values: revenue (17 rows, 3.4%), customer_rating (29 rows, 5.8%)

3. Key Findings and Insights
- Average units sold: 246.88 with high variability (std: 142.66)
- Revenue ranges from $145.86 to $9,979.55
- No strong correlations found between numeric variables
- Gadget Y is the top-selling product (148 occurrences)

4. Recommendations
- Implement data collection improvements for customer_rating field
- Investigate revenue variability across products and regions
- Focus marketing efforts on North region (highest sales concentration)

5. Next Steps
- Fix missing data in revenue and customer_rating columns
- Conduct deeper product-level and region-level analysis
- Set up automated data quality monitoring

