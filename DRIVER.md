# DRIVER Protocol Documentation: LULU DCF Valuation Tool

This project was built using the **DRIVER** methodology: Define, Represent, Implement, Validate, Evolve, and Reflect.

## 1. Define
**Objective**: Build a Python-based Discounted Cash Flow (DCF) valuation tool for the ticker LULU (Lululemon Athletica Inc.).
**Requirements**: The tool must fetch the last 3 years of Free Cash Flow and Shares Outstanding, implements a 5-year DCF projection based on adjustable Weighted Average Cost of Capital (WACC) and Terminal Growth Rate, and generate a 5x5 matrix showing implied stock prices across WACC and Growth rate combinations.

## 2. Represent
**Structure & Technology**: Python was chosen as the primary language. 
- The project structure initially consisted of a `main.py` script and a `requirements.txt`.
- Data Fetching: We utilize `yfinance` to interact with Yahoo Finance APIs to pull the latest ticker information.
- Financial Math: We employ standard formulas to execute Present Value calculation of projected Cash Flows and Terminal Value.
- Matrix Generation: `pandas` DataFrames are used to neatly tabulate sensitivity data, aided by `numpy`.
- Web UI: Subsequently introduced `streamlit` through `app.py` for interactive visualization.

## 3. Implement
**Development Stages**:
- **Phase A**: Created `main.py` focusing on terminal execution. Built the `get_lulu_data`, `calculate_implied_price`, and `generate_sensitivity_table` functions to process data cleanly.
- **Phase B**: Set up the Python virtual environment (`.venv`) to securely install `yfinance`, `pandas`, and `numpy`.
- **Phase C**: Transitioned the solution into an interactive web interface by coding `app.py` using `streamlit`. Bound the model variables to interactive sidebar sliders and presented the final output using Streamlit metrics and dataframes.

## 4. Validate
**Functionality Check**:
- Confirmed `yfinance` effectively pulls the most recent FCF and Total Debt/Cash to derive Net Debt.
- Validated that the DCF calculation correctly accounts for PV of FCFs over 5 years.
- Validated that the 5x5 Matrix correctly displays N/A in scenarios where the Terminal Growth rate exceeds or equals the WACC (which would infinitely compound value).
- *Challenge Encountered*: Mac Xcode license agreements temporarily blocked terminal installations, which was immediately bypassed using `sudo xcodebuild -license accept`.

## 5. Evolve
**Iterative Enhancements**: 
- The model evolved rapidly from a static terminal script (`main.py`) to an interactive, web-deployable dashboard (`app.py`). 
- A bar chart was added to visualize historical Free Cash Flow dynamically based on pulled data.
- Implemented caching (`@st.cache_data`) in `app.py` to prevent repeated and unnecessary API calls to Yahoo Finance when users adjust the sliders, improving performance drastically.

## 6. Reflect
**Insights**:
- **Data Reliability**: Relying on free APIs like `yfinance` can sometimes result in missing data keys (e.g. `sharesOutstanding` vs `impliedSharesOutstanding`). Resilient `if/else` logic is required to ensure the model doesn't crash.
- **UX Impact**: Switching from terminal execution to Streamlit vastly improved the tool's accessibility, proving that complex financial formulas are best presented through interactive, visual mediums. Adjusting assumptions instantly reflects in the color-coded sensitivity table, offering immediate insights.
