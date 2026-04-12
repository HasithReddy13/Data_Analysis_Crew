import pandas as pd
import numpy as np
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import json


# defines what input the tool expects - just a file path
class StatisticalProfilerInput(BaseModel):
    file_path: str = Field(description="Path to the CSV file to profile")


class StatisticalProfilerTool(BaseTool):
    """
    Custom tool that takes a CSV file and returns a full statistical profile.
    This is the main custom tool for the assignment - we built this from scratch
    to handle data profiling automatically instead of writing pandas code manually.
    
    It checks for: data types, missing values, basic stats, correlations,
    categorical breakdowns, outliers, and gives an overall quality score.
    """

    name: str = "Statistical Profiler"
    description: str = (
        "Analyzes a CSV dataset and returns a comprehensive statistical profile "
        "including data types, missing values, basic statistics, correlations, "
        "and data quality score. Use this tool when you need to understand "
        "the structure and quality of a dataset."
    )
    args_schema: Type[BaseModel] = StatisticalProfilerInput

    def _run(self, file_path: str) -> str:
        # try to load the file, return a clear error if something goes wrong
        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            return f"Error: File '{file_path}' not found."
        except Exception as e:
            return f"Error reading file: {str(e)}"

        # this dict will hold everything we find about the dataset
        profile = {
            "overview": {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
            },
            "data_types": {},
            "missing_values": {},
            "numeric_stats": {},
            "categorical_stats": {},
            "correlations": {},
            "data_quality_score": 0
        }

        # grab the data type for each column
        for col in df.columns:
            profile["data_types"][col] = str(df[col].dtype)

        # check each column for missing values
        # we track both the raw count and the percentage
        total_cells = len(df) * len(df.columns)
        total_missing = 0
        for col in df.columns:
            missing = int(df[col].isnull().sum())
            pct = round(missing / len(df) * 100, 2)
            profile["missing_values"][col] = {"count": missing, "percentage": pct}
            total_missing += missing

        # for numeric columns, calculate the standard descriptive stats
        # also checking skewness and counting outliers using the 3-sigma rule
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            profile["numeric_stats"][col] = {
                "mean": round(float(df[col].mean()), 2),
                "median": round(float(df[col].median()), 2),
                "std": round(float(df[col].std()), 2),
                "min": round(float(df[col].min()), 2),
                "max": round(float(df[col].max()), 2),
                "skewness": round(float(df[col].skew()), 2),
                # anything more than 3 standard deviations from the mean counts as an outlier
                "outliers": int(((df[col] - df[col].mean()).abs() > 3 * df[col].std()).sum())
            }

        # for text/category columns, see how many unique values there are
        # and which value shows up the most
        cat_cols = df.select_dtypes(include=["object", "category"]).columns
        for col in cat_cols:
            profile["categorical_stats"][col] = {
                "unique_values": int(df[col].nunique()),
                "top_value": str(df[col].mode()[0]) if not df[col].mode().empty else "N/A",
                "top_frequency": int(df[col].value_counts().iloc[0]) if len(df[col].value_counts()) > 0 else 0
            }

        # look for strong correlations between numeric columns
        # only flagging pairs where the absolute correlation is above 0.7
        if len(numeric_cols) > 1:
            corr = df[numeric_cols].corr()
            strong = []
            for i in range(len(corr.columns)):
                for j in range(i + 1, len(corr.columns)):
                    val = corr.iloc[i, j]
                    if abs(val) > 0.7:
                        strong.append({
                            "pair": f"{corr.columns[i]} & {corr.columns[j]}",
                            "correlation": round(float(val), 3)
                        })
            profile["correlations"]["strong_correlations"] = strong

        # calculate an overall quality score
        # weighting: 70% based on how complete the data is, 30% on how unique the rows are
        # a dataset with lots of missing values or tons of duplicates gets a lower score
        completeness = (1 - total_missing / total_cells) * 100 if total_cells > 0 else 100
        duplicate_pct = (df.duplicated().sum() / len(df)) * 100 if len(df) > 0 else 0
        quality = round(completeness * 0.7 + (100 - duplicate_pct) * 0.3, 1)
        profile["data_quality_score"] = quality

        return json.dumps(profile, indent=2)
