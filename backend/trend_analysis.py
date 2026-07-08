import pandas as pd

def get_weekly_trends():
    # Load your specific project dataset
    df = pd.read_csv("data/final_dataset.csv")
    
    # Ensure date column is datetime format
    df["date"] = pd.to_datetime(df["date"])
    
    # Group by week and calculate the mean of your key metrics
    weekly = df.groupby(pd.Grouper(key="date", freq="W"))[[
        "overall_score", "steps", "avg_hr", "sleep_duration_h"
    ]].mean()
    
    # Ensure we have at least 2 weeks to compare
    if len(weekly) >= 2:
        current = weekly.iloc[-1]
        previous = weekly.iloc[-2]
        
        # Calculate percentage change: ((New - Old) / Old) * 100
        change = ((current - previous) / previous) * 100
        return weekly, change
    
    return weekly, None

# Run the analysis
if __name__ == "__main__":
    trends, change = get_weekly_trends()
    print("--- Weekly Averages (Last 5 Weeks) ---")
    print(trends.tail())
    
    if change is not None:
        print("\n--- Percentage Change (Last Week vs Previous) ---")
        print(change)
    else:
        print("\nNot enough data to calculate week-to-week change.")