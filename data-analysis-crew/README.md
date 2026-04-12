# Data Analysis Crew - Multi-Agent AI System

An intelligent multi-agent data analysis system built with **CrewAI** and powered by **Ollama (LLaMA 3.1)**. The system automates the entire data analysis pipeline — from dataset profiling and quality assessment to insight generation and executive report writing — using three specialized AI agents working in coordination.

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Agents](#agents)
- [Tools](#tools)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Sample Output](#sample-output)
- [Known Limitations](#known-limitations)
- [Future Improvements](#future-improvements)

---

## Overview

This project demonstrates the design and implementation of an **agentic AI system** where multiple AI agents collaborate to complete a complex data analysis workflow. A controller agent orchestrates two specialized agents — a Data Engineer and a Data Analyst — each equipped with specific tools to perform their tasks.

The system follows a **sequential orchestration pattern** where:
1. The Data Engineer profiles the dataset using custom and built-in tools
2. The Data Analyst interprets the findings and generates business insights
3. The Data Analysis Manager compiles everything into a polished executive report

### Key Features

- Multi-agent orchestration with clear role separation
- Custom Statistical Profiler tool for automated dataset analysis
- Sequential task execution with context passing between agents
- Automated report generation saved to markdown
- Runs entirely locally using Ollama — no paid API keys required

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INPUT                            │
│              (CSV Dataset Path)                          │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              CREWAI ORCHESTRATOR                         │
│            (Sequential Process)                          │
└─────────────────┬───────────────────────────────────────┘
                  │
      ┌───────────┼───────────────┐
      ▼           ▼               ▼
┌───────────┐ ┌───────────┐ ┌──────────────┐
│   TASK 1  │ │   TASK 2  │ │    TASK 3    │
│ Profiling │ │ Analysis  │ │ Final Report │
└─────┬─────┘ └─────┬─────┘ └──────┬───────┘
      │             │              │
      ▼             ▼              ▼
┌───────────┐ ┌───────────┐ ┌──────────────┐
│   DATA    │ │   DATA    │ │   ANALYSIS   │
│ ENGINEER  │ │  ANALYST  │ │   MANAGER    │
│  Agent    │ │  Agent    │ │  (Controller │
│           │ │           │ │    Agent)    │
├───────────┤ ├───────────┤ ├──────────────┤
│  Tools:   │ │  Tools:   │ │  Tools:      │
│ -Profiler │ │ -FileRead │ │  None        │
│ -FileRead │ │           │ │ (writes from │
│ -DirRead  │ │           │ │  context)    │
└─────┬─────┘ └─────┬─────┘ └──────┬───────┘
      │             │              │
      ▼             ▼              ▼
┌─────────────────────────────────────────────────────────┐
│                 OUTPUT                                   │
│          outputs/final_report.md                         │
└─────────────────────────────────────────────────────────┘
```

---

## Agents

### 1. Data Analysis Manager (Controller Agent)
- **Role**: Orchestrates the workflow and writes the final executive summary
- **Capabilities**: Compiles findings from other agents into a structured report
- **Delegation**: Disabled — writes reports directly from provided context

### 2. Data Engineer
- **Role**: Profiles datasets and assesses data quality
- **Tools**: Statistical Profiler (custom), FileReadTool, DirectoryReadTool
- **Capabilities**: Runs automated profiling, identifies missing values, data types, outliers, and correlations

### 3. Data Analyst
- **Role**: Interprets profiling results and generates business insights
- **Tools**: FileReadTool
- **Capabilities**: Identifies trends, patterns, and provides actionable business recommendations

---

## Tools

### Custom Tool: Statistical Profiler

A purpose-built tool that performs comprehensive dataset profiling:

| Feature | Description |
|---------|-------------|
| **Overview** | Row count, column count, column names, memory usage |
| **Data Types** | Type detection for each column |
| **Missing Values** | Count and percentage per column |
| **Numeric Stats** | Mean, median, std, min, max, skewness, outlier count |
| **Categorical Stats** | Unique values, most frequent value and its count |
| **Correlations** | Identifies strong correlations (\|r\| > 0.7) between numeric columns |
| **Quality Score** | Composite score based on completeness (70%) and uniqueness (30%) |

**Input**: File path to a CSV file  
**Output**: JSON object with all profiling results

### Built-in Tools

| Tool | Purpose |
|------|---------|
| **FileReadTool** | Reads raw data files for inspection and verification |
| **DirectoryReadTool** | Lists available files in the data directory for discovery |

---

## Installation

### Prerequisites

- Python 3.12 or higher
- [Ollama](https://ollama.com) installed on your machine
- At least 8GB RAM (16GB recommended)

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd data-analysis-crew

# 2. Create and activate virtual environment
python3.12 -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Pull the LLM model
ollama pull llama3.1:8b

# 5. Generate sample dataset (optional — already included)
python data/create_sample.py
```

---

## Usage

### 1. Start the Ollama server

Open a separate terminal and run:

```bash
ollama serve
```

### 2. Run the analysis system

```bash
python main.py
```

### 3. View the output

The final report is saved to `outputs/final_report.md` and also printed to the terminal.

---

## Project Structure

```
data-analysis-crew/
│
├── main.py                          # Main entry point — defines agents, tasks, and crew
│
├── tools/
│   ├── __init__.py
│   └── statistical_profiler.py      # Custom Statistical Profiler tool
│
├── data/
│   ├── create_sample.py             # Script to generate sample sales data
│   └── sales_data.csv               # Sample dataset (500 rows, 7 columns)
│
├── outputs/
│   └── final_report.md              # Generated executive summary report
│
├── docs/
│   └── report.pdf                   # Technical documentation
│
├── requirements.txt                 # Python dependencies
├── requirements_full.txt            # Complete pip freeze output
└── README.md                        # This file
```

---

## Sample Output

The system generates an executive summary report with five sections:

1. **Executive Summary** — High-level overview of findings
2. **Data Overview and Quality Assessment** — Dataset size, quality score, missing values
3. **Key Findings and Insights** — Trends, patterns, and correlations
4. **Recommendations** — Three actionable business recommendations
5. **Next Steps** — Immediate actions to take

---

## Known Limitations

1. **Local LLM Accuracy**: The LLaMA 3.1 8B model running locally may hallucinate statistics instead of using exact numbers from tool outputs. A larger model or cloud-based LLM would improve accuracy.
2. **No Real-time Web Search**: The system does not include a web search tool due to API key requirements. Future versions could integrate search for contextual industry data.
3. **Single Dataset Format**: Currently supports only CSV files. Future versions could support Excel, JSON, and database connections.
4. **Sequential Only**: Tasks run sequentially. Parallel execution of independent tasks could improve performance.

---

## Future Improvements

- Integrate a cloud LLM (GPT-4, Gemini) for improved response accuracy
- Add web search capability for industry benchmarking
- Support multiple file formats (Excel, Parquet, JSON)
- Implement parallel task execution for faster processing
- Add visualization agent for automated chart generation
- Build a web-based UI for non-technical users

---

## Technologies Used

- **CrewAI** — Multi-agent orchestration framework
- **Ollama** — Local LLM inference
- **LLaMA 3.1 8B** — Large language model
- **Pandas & NumPy** — Data processing
- **Python 3.12** — Programming language

---

## Author

Hasith Reddy Rapolu  
Northeastern University  
Big Data Architecture and Management
