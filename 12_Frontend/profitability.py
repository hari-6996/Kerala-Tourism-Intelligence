from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

BUSINESS_PRESETS = {
    "Resort": {
        "investment": 10000000,   # ₹1 Crore
        "monthly_revenue": 550000, # ₹5.5 Lakhs
        "monthly_expenses": 320000 # ₹3.2 Lakhs
    },
    "Hotel": {
        "investment": 7500000,    # ₹75 Lakhs
        "monthly_revenue": 420000, # ₹4.2 Lakhs
        "monthly_expenses": 250000 # ₹2.5 Lakhs
    },
    "Homestay": {
        "investment": 2500000,    # ₹25 Lakhs
        "monthly_revenue": 160000, # ₹1.6 Lakhs
        "monthly_expenses": 75000  # ₹75,000
    },
    "Restaurant": {
        "investment": 3500000,    # ₹35 Lakhs
        "monthly_revenue": 300000, # ₹3 Lakhs
        "monthly_expenses": 190000 # ₹1.9 Lakhs
    }
}

def calculate_profitability(
    investment: float,
    monthly_revenue: float,
    monthly_expenses: float
) -> Dict[str, Any]:
    if investment <= 0:
        return {
            "monthly_profit": 0.0,
            "annual_profit": 0.0,
            "payback_months": None,
            "payback_years": None,
            "annual_roi": 0.0,
            "is_profitable": False,
            "status_message": "Initial investment must be greater than zero."
        }

    monthly_profit = monthly_revenue - monthly_expenses
    annual_profit = monthly_profit * 12.0
    is_profitable = monthly_profit > 0

    if is_profitable:
        payback_months = investment / monthly_profit
        payback_years = payback_months / 12.0
        status_message = "Positive operating margins projected."
    elif monthly_profit == 0:
        payback_months = None
        payback_years = None
        status_message = "Breakeven operation (zero net monthly profit)."
    else:
        payback_months = None
        payback_years = None
        status_message = "Negative operating cash flow. Expenses exceed revenues."

    annual_roi = (annual_profit / investment) * 100.0

    return {
        "monthly_profit": monthly_profit,
        "annual_profit": annual_profit,
        "payback_months": payback_months,
        "payback_years": payback_years,
        "annual_roi": annual_roi,
        "is_profitable": is_profitable,
        "status_message": status_message
    }

def generate_cash_flow_projection(
    investment: float,
    monthly_profit: float,
    years: int = 5
) -> pd.DataFrame:
    data = []
    cumulative = -investment
    annual_profit = monthly_profit * 12.0

    data.append({
        "Year": "Year 0 (Initial)",
        "Year_Num": 0,
        "Annual_Cash_Flow": -investment,
        "Cumulative_Cash_Flow": cumulative,
        "Net_Position": "Initial Outlay"
    })

    for y in range(1, years + 1):
        cumulative += annual_profit
        data.append({
            "Year": f"Year {y}",
            "Year_Num": y,
            "Annual_Cash_Flow": annual_profit,
            "Cumulative_Cash_Flow": cumulative,
            "Net_Position": "Profitable" if cumulative >= 0 else "Recovering"
        })

    return pd.DataFrame(data)

def format_inr(val: Optional[float], decimals: int = 0) -> str:
    if val is None or np.isnan(val):
        return "N/A"
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 10000000:
        return f"{sign}₹{abs_val / 10000000:.2f} Cr"
    elif abs_val >= 100000:
        return f"{sign}₹{abs_val / 100000:.2f} L"
    elif abs_val >= 1000:
        return f"{sign}₹{abs_val / 1000:.1f} K"
    else:
        return f"{sign}₹{abs_val:,.{decimals}f}"
