from prophet import Prophet
import pandas as pd

def forecast_cost(df, periods=3):
    df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce")
    df = df.dropna(subset=["Cost"])

    # Combine Year and Month to create Date
    df["Month"] = df["Month"].astype(str).str.zfill(2)
    df["Date"] = pd.to_datetime(df["Year"].astype(str) + "-" + df["Month"])

    # Aggregate total cost per month
    monthly_cost = df.groupby("Date")["Cost"].sum().reset_index()
    monthly_cost.rename(columns={"Date": "ds", "Cost": "y"}, inplace=True)

    # Fit the model
    model = Prophet()
    model.fit(monthly_cost)

    # Make future dataframe and forecast
    future = model.make_future_dataframe(periods=periods, freq='M')
    forecast = model.predict(future)

    # Filter only forecasted months (not in original)
    
    forecast_future = forecast[forecast["ds"] > monthly_cost["ds"].max()]
    forecast_output = forecast_future[["ds", "yhat", "yhat_lower", "yhat_upper"]].to_dict(orient="records")

    return forecast_output

