import yfinance as yf
import pandas as pd
import numpy as np

# --- USER INPUTS ---
TICKER = "LULU"
wacc = 0.09                # Default WACC
terminal_growth = 0.02     # Default Terminal Growth Rate
PROJECTION_YEARS = 5       # 5-year DCF projection
FCF_GROWTH_RATE = 0.10     # Assumed annual FCF growth for the projection period
# -------------------

def get_lulu_data(ticker_symbol):
    print(f"Fetching data for {ticker_symbol} from Yahoo Finance...")
    ticker = yf.Ticker(ticker_symbol)
    
    # 1. Get Free Cash Flow (last 3 years)
    cash_flow = ticker.cashflow
    if 'Free Cash Flow' in cash_flow.index:
        fcf_series = cash_flow.loc['Free Cash Flow'].dropna()
    else:
        # Calculate manually if 'Free Cash Flow' is missing
        operating_cf = cash_flow.loc['Operating Cash Flow'] if 'Operating Cash Flow' in cash_flow.index else cash_flow.loc['Total Cash From Operating Activities']
        capex = cash_flow.loc['Capital Expenditure'] if 'Capital Expenditure' in cash_flow.index else pd.Series(0, index=operating_cf.index)
        fcf_series = operating_cf + capex  # capex is typically represented as a negative number
        
    fcf_last_3_yr = fcf_series.head(3)
    
    # 2. Get Shares Outstanding
    shares_outstanding = ticker.info.get('sharesOutstanding')
    if not shares_outstanding:
        shares_outstanding = ticker.info.get('impliedSharesOutstanding', 1) # Fallback
        
    # 3. Get Current Price
    current_price = ticker.info.get('currentPrice', ticker.info.get('regularMarketPrice', 0))
    
    # 4. Get Net Debt (Total Debt - Cash And Cash Equivalents)
    balance_sheet = ticker.balance_sheet
    total_debt = 0
    if 'Total Debt' in balance_sheet.index:
        total_debt = balance_sheet.loc['Total Debt'].iloc[0]
    elif 'Long Term Debt' in balance_sheet.index:
        total_debt = balance_sheet.loc['Long Term Debt'].iloc[0]
        if 'Short Long Term Debt' in balance_sheet.index:
            total_debt += balance_sheet.loc['Short Long Term Debt'].iloc[0]
            
    cash = 0
    if 'Cash And Cash Equivalents' in balance_sheet.index:
        cash = balance_sheet.loc['Cash And Cash Equivalents'].iloc[0]
        
    net_debt = total_debt - cash

    return fcf_last_3_yr, shares_outstanding, current_price, net_debt

def calculate_implied_price(recent_fcf, shares, net_debt, calc_wacc, calc_terminal_growth):
    """Calculates the Implied Share Price using a 5-year DCF Model."""
    # Start projection from the most recent FCF
    base_fcf = recent_fcf.iloc[0]
    
    # 1. Project FCF for 5 years
    projected_fcfs = []
    for i in range(1, PROJECTION_YEARS + 1):
        projected_fcf = base_fcf * ((1 + FCF_GROWTH_RATE) ** i)
        projected_fcfs.append(projected_fcf)
        
    # 2. Calculate Present Value (PV) of Projected FCFs
    pv_fcfs = []
    for i, fcf in enumerate(projected_fcfs):
        pv = fcf / ((1 + calc_wacc) ** (i + 1))
        pv_fcfs.append(pv)
        
    sum_pv_fcfs = sum(pv_fcfs)
    
    # 3. Calculate Terminal Value (TV) & PV of Terminal Value
    terminal_value = (projected_fcfs[-1] * (1 + calc_terminal_growth)) / (calc_wacc - calc_terminal_growth)
    pv_terminal_value = terminal_value / ((1 + calc_wacc) ** PROJECTION_YEARS)
    
    # 4. Calculate Enterprise Value (EV) and Equity Value
    enterprise_value = sum_pv_fcfs + pv_terminal_value
    equity_value = enterprise_value - net_debt
    
    # 5. Implied Share Price
    implied_price = equity_value / shares
    
    return implied_price

def generate_sensitivity_table(recent_fcf, shares, net_debt):
    """Generates a 5x5 Matrix Sensitivity Table for WACC and Terminal Growth."""
    print("\n--- Generating 5x5 Sensitivity Matrix ---")
    
    # WACC intervals: 8% to 12% (5 steps)
    wacc_rates = [0.08, 0.09, 0.10, 0.11, 0.12]
    # Growth intervals: 1% to 4% (5 steps)
    growth_rates = np.linspace(0.01, 0.04, 5)
    
    # Initialize an empty DataFrame
    df = pd.DataFrame(index=[f"{w*100:.1f}%" for w in wacc_rates], 
                      columns=[f"{g*100:.2f}%" for g in growth_rates])
    df.index.name = "WACC ↓ / Growth →"
    
    # Populate the table
    for i, w in enumerate(wacc_rates):
        for j, g in enumerate(growth_rates):
            price = calculate_implied_price(recent_fcf, shares, net_debt, calc_wacc=w, calc_terminal_growth=g)
            df.iloc[i, j] = price
            
    return df

def main():
    print(f"=== DCF Valuation Model for {TICKER} ===\n")
    
    # Fetch Data
    fcf_history, shares, current_price, net_debt = get_lulu_data(TICKER)
    
    print("\n--- Recent Financial Data ---")
    print(f"Current Stock Price: ${current_price:,.2f}")
    if pd.isna(shares) or shares is None:
        print("Shares Outstanding:  Data Unavailable")
        return
    else:
        print(f"Shares Outstanding:  {shares:,.0f}")
        
    print(f"Net Debt:            ${net_debt:,.0f}")
    print("Last 3 Years Free Cash Flow:")
    for date, val in fcf_history.items():
        if hasattr(date, 'strftime'):
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = str(date)
        print(f"  {date_str}: ${val:,.0f}")
        
    # Calculate Base DCF using User Inputs
    print("\n--- DCF Valuation (Base Case) ---")
    print(f"Assumed WACC: {wacc*100:.1f}%")
    print(f"Assumed Terminal Growth: {terminal_growth*100:.1f}%")
    
    implied_share_price = calculate_implied_price(
        recent_fcf=fcf_history, 
        shares=shares, 
        net_debt=net_debt, 
        calc_wacc=wacc, 
        calc_terminal_growth=terminal_growth
    )
    
    print(f"\n>> Base Implied Share Price: ${implied_share_price:,.2f} <<")
    
    # Generate Sensitivity Table
    sensitivity_table = generate_sensitivity_table(fcf_history, shares, net_debt)
    
    # Format the table for display
    pd.options.display.float_format = '${:,.2f}'.format
    print("\nImplied Stock Price based on WACC & Terminal Growth Rates:")
    print(sensitivity_table)
    
if __name__ == "__main__":
    main()
