# LULU DCF Valuation Tool

A Python-based, interactive Discounted Cash Flow (DCF) model built specifically for valuing Lululemon Athletica Inc. (LULU) using live financial data.

## Features
- **Live Data Fetching**: Retrieves real-time stock price, shares outstanding, net debt, and historical free cash flow directly from Yahoo Finance.
- **Interactive Web Interface**: Uses Streamlit to provide a clean, modern UI with sliders for key assumptions (WACC, Terminal Growth Rate, Projection Years, FCF Growth Rate).
- **Core Valuation Engine**: Calculates Present Value (PV) of projected FCFs and Terminal Value to arrive at an implied share price.
- **Dynamic Sensitivity Analysis**: Instantly generates a color-coded 5x5 sensitivity matrix showing implied stock prices across varying WACC and Terminal Growth rate scenarios.

## Technologies Used
- **Python**: Core logic
- **Streamlit**: Interactive web UI
- **yfinance**: Real-time market data retrieval
- **pandas & numpy**: Financial calculations and matrix generation

## Getting Started

### Prerequisites
- Python 3.8+ installed on your system.
- MacOS Users: Ensure you have accepted the Xcode command-line tools license (`sudo xcodebuild -license accept`).

### Installation
1. Clone the repository and navigate into the project directory:
   ```bash
   cd lulu_dcf
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

**Option 1: Interactive Web App (Recommended)**  
Launch the Streamlit web application for the full interactive experience:
```bash
streamlit run app.py
```
This will automatically open the application in your default web browser (typically at `http://localhost:8501`).

**Option 2: Terminal Output**  
If you prefer a text-based output directly in the console, you can run the core logic file:
```bash
python main.py
```

## How It Works
1. **Inputs**: The model dynamically takes your assumptions for WACC (Discount Rate), Terminal Growth Rate, Projection timeline (e.g., 5 years), and assumed FCF Growth Rate.
2. **Current State**: It pulls LULU's most recent Free Cash Flow, Current Stock Price, Net Debt, and Shares Outstanding.
3. **Projection**: It projects FCF forward based on the assumed growth rate and discounts it back to the present value using the specified WACC.
4. **Conclusion**: It calculates the Enterprise Value, subtracts Net Debt to get Equity Value, and divides by shares outstanding to present an Implied Share Price, which is then compared against the actual current stock price.

## Disclaimer
*This tool is for educational and informational purposes only and should not be considered financial advice. Always do your own research before making investment decisions.*
