import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="LULU DCF Valuation Tool", layout="wide")

st.title("💸 LULU DCF Valuation Tool")
st.markdown("Interactive Discounted Cash Flow (DCF) model for Lululemon Athletica Inc. (LULU).")

# --- SIDEBAR FOR INPUTS ---
st.sidebar.header("Assumptions & Inputs")
wacc = st.sidebar.slider("WACC (Discount Rate)", min_value=0.05, max_value=0.15, value=0.09, step=0.005, format="%.3f")
terminal_growth = st.sidebar.slider("Terminal Growth Rate", min_value=0.00, max_value=0.05, value=0.02, step=0.005, format="%.3f")
projection_years = st.sidebar.number_input("Projection Years", min_value=1, max_value=10, value=5)
fcf_growth_rate = st.sidebar.slider("Assumed FCF Growth Rate", min_value=-0.05, max_value=0.25, value=0.10, step=0.01)

# Function to fetch data, cached so we don't spam Yahoo Finance
@st.cache_data(ttl=3600)
def get_lulu_data(ticker_symbol="LULU"):
    ticker = yf.Ticker(ticker_symbol)
    
    # 1. Get Free Cash Flow
    cash_flow = ticker.cashflow
    if 'Free Cash Flow' in cash_flow.index:
        fcf_series = cash_flow.loc['Free Cash Flow'].dropna()
    else:
        operating_cf = cash_flow.loc['Operating Cash Flow'] if 'Operating Cash Flow' in cash_flow.index else cash_flow.loc['Total Cash From Operating Activities']
        capex = cash_flow.loc['Capital Expenditure'] if 'Capital Expenditure' in cash_flow.index else pd.Series(0, index=operating_cf.index)
        fcf_series = operating_cf + capex
        
    fcf_last_3_yr = fcf_series.head(3)
    
    # 2. Shares
    shares = ticker.info.get('sharesOutstanding') or ticker.info.get('impliedSharesOutstanding', 1)
        
    # 3. Price
    price = ticker.info.get('currentPrice', ticker.info.get('regularMarketPrice', 0))
    
    # 4. Net Debt
    balance_sheet = ticker.balance_sheet
    total_debt = 0
    if 'Total Debt' in balance_sheet.index:
        total_debt = balance_sheet.loc['Total Debt'].iloc[0]
    elif 'Long Term Debt' in balance_sheet.index:
        total_debt = balance_sheet.loc['Long Term Debt'].iloc[0]
        if 'Short Long Term Debt' in balance_sheet.index:
            total_debt += balance_sheet.loc['Short Long Term Debt'].iloc[0]
            
    cash = balance_sheet.loc['Cash And Cash Equivalents'].iloc[0] if 'Cash And Cash Equivalents' in balance_sheet.index else 0
    net_debt = total_debt - cash

    return fcf_last_3_yr, shares, price, net_debt

# Fetch the data
try:
    with st.spinner("Fetching financial data from Yahoo Finance..."):
        fcf_history, shares, current_price, net_debt = get_lulu_data()
        
    st.success("Data fetched successfully!")
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

def calculate_implied_price(recent_fcf, shares_out, net_d, calc_wacc, calc_terminal_growth):
    base_fcf = recent_fcf.iloc[0]
    
    # 1. Project FCF
    projected_fcfs = [base_fcf * ((1 + fcf_growth_rate) ** i) for i in range(1, projection_years + 1)]
        
    # 2. PV of FCFs
    pv_fcfs = [fcf / ((1 + calc_wacc) ** (i + 1)) for i, fcf in enumerate(projected_fcfs)]
    sum_pv_fcfs = sum(pv_fcfs)
    
    # 3. Terminal Value
    terminal_value = (projected_fcfs[-1] * (1 + calc_terminal_growth)) / (calc_wacc - calc_terminal_growth) if calc_wacc > calc_terminal_growth else 0
    pv_terminal_value = terminal_value / ((1 + calc_wacc) ** projection_years)
    
    # 4. EV & Equity Value
    enterprise_value = sum_pv_fcfs + pv_terminal_value
    equity_value = enterprise_value - net_d
    
    # 5. Implied Price
    return equity_value / shares_out

# Main Content Layout
col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Stock Price", f"${current_price:,.2f}")
col2.metric("Shares Outstanding", f"{shares:,.0f}" if shares > 1 else "N/A")
col3.metric("Net Debt", f"${net_debt:,.0f}")
most_recent_fcf_date = fcf_history.index[0].strftime('%Y-%m-%d') if hasattr(fcf_history.index[0], 'strftime') else str(fcf_history.index[0])
col4.metric(f"Most Recent FCF ({most_recent_fcf_date})", f"${fcf_history.iloc[0]:,.0f}")

st.divider()

# --- Base DCF Calculation ---
implied_share_price = calculate_implied_price(fcf_history, shares, net_debt, wacc, terminal_growth)

st.header("Valuation Summary")
metric_col1, metric_col2 = st.columns(2)
metric_col1.metric("Implied Share Price (Base)", f"${implied_share_price:,.2f}", 
                   delta=f"{((implied_share_price / current_price) - 1) * 100:.1f}% vs Current", 
                   delta_color="normal" if implied_share_price > current_price else "inverse")

st.divider()

# --- Sensitivity Table ---
st.header("Sensitivity Analysis")
st.markdown("Implied Stock Price based on varying **WACC (Rows)** and **Terminal Growth Rates (Columns)**.")

@st.cache_data
def generate_sensitivity_table(fcf_data, s_out, n_debt, base_wacc, base_tg):
    # WACC variations (+/- 2% from base)
    wacc_rates = [max(0.01, base_wacc + i * 0.01) for i in range(-2, 3)]
    # Growth variations (+/- 1% from base, step 0.5%)
    growth_rates = [max(0.0, base_tg + i * 0.005) for i in range(-2, 3)]
    
    df = pd.DataFrame(index=[f"{w*100:.1f}%" for w in wacc_rates], 
                      columns=[f"{g*100:.2f}%" for g in growth_rates])
    
    for i, w in enumerate(wacc_rates):
        for j, g in enumerate(growth_rates):
            if w <= g:
                df.iloc[i, j] = np.nan # Invalid DCF condition
            else:
                price = calculate_implied_price(fcf_data, s_out, n_debt, w, g)
                df.iloc[i, j] = price
    return df

with st.spinner("Generating Sensitivity Matrix..."):
    sens_df = generate_sensitivity_table(fcf_history, shares, net_debt, wacc, terminal_growth)
    
    # Display the dataframe with pandas styling
    st.dataframe(sens_df.style.format(na_rep="N/A", formatter="${:,.2f}")\
                 .background_gradient(cmap="RdYlGn", axis=None), 
                 use_container_width=True)

st.caption("Note: Cells with N/A indicate scenarios where Terminal Growth >= WACC, which invalidates the perpetuity growth formula.")

# Historical FCF Chart
st.subheader("Historical Free Cash Flow")
fcf_df = pd.DataFrame(fcf_history).reset_index()
fcf_df.columns = ['Date', 'Free Cash Flow']
st.bar_chart(data=fcf_df, x='Date', y='Free Cash Flow')
