import pandas as pd
import numpy as np

# seed so the dataset is the same every time we run this
np.random.seed(42)
n = 500

# building a fake sales dataset with 7 columns
# tried to make it realistic - daily sales records with products, regions, etc.
data = {
    "date": pd.date_range("2023-01-01", periods=n, freq="D"),
    "product": np.random.choice(["Widget A", "Widget B", "Gadget X", "Gadget Y"], n),
    "region": np.random.choice(["North", "South", "East", "West"], n),
    "units_sold": np.random.randint(10, 500, n),
    "revenue": np.random.uniform(100, 10000, n).round(2),
    "customer_rating": np.random.uniform(1, 5, n).round(1),
    "return_rate": np.random.uniform(0, 0.3, n).round(3),
}

df = pd.DataFrame(data)

# intentionally adding some missing values so the profiler has something to detect
# about 5% of customer_rating and 3% of revenue will be null
mask = np.random.random(n) < 0.05
df.loc[mask, "customer_rating"] = np.nan
mask2 = np.random.random(n) < 0.03
df.loc[mask2, "revenue"] = np.nan

df.to_csv("data/sales_data.csv", index=False)
print(f"Created sales_data.csv with {n} rows")
