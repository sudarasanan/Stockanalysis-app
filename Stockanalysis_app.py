import streamlit as st
import yfinance as yf
import pandas as pd

# Set page config
st.set_page_config(page_title="Indian Stock Analyzer", layout="wide")

def get_stock_info(symbol):
    ticker = yf.Ticker(symbol)
    return ticker

def analyze_capital_allocation(ticker):
    """Analyzes how well management spends money."""
    balance_sheet = ticker.balance_sheet
    cash_flow = ticker.cashflow
    
    try:
        # Simple ROIC Proxy = EBIT / (Debt + Equity)
        info = ticker.info
        roic = info.get('returnOnAssets', 0) * 100 # Simplified proxy
        div_yield = info.get('dividendYield', 0)
        
        analysis = f"**ROIC/ROA:** {roic:.2f}% \n\n"
        if roic > 15:
            analysis += "✅ **Efficient:** Management generates high returns on capital."
        else:
            analysis += "⚠️ **Warning:** Capital returns are below ideal thresholds (15%)."
        return analysis
    except:
        return "Data insufficient for Capital Allocation analysis."

def analyze_integrity(ticker):
    """Proxies for Management Integrity using Cash Flow vs Net Income."""
    try:
        income = ticker.financials
        cf = ticker.cashflow
        
        net_income = income.loc['Net Income'].iloc[0]
        cash_from_ops = cf.loc['Cash Flow From Operating Activities'].iloc[0]
        
        ratio = cash_from_ops / net_income
        
        analysis = f"**CFO / Net Income Ratio:** {ratio:.2f}\n\n"
        if ratio >= 1.0:
            analysis += "✅ **High Integrity:** Reported profits are backed by actual cash."
        else:
            analysis += "⚠️ **Red Flag:** Profits are significantly higher than cash flow; check for aggressive accounting."
        return analysis
    except:
        return "Data insufficient for Integrity analysis."

# --- UI Layout ---
st.title("📈 Indian Stock Fundamental Analyzer")
st.markdown("Analyze NSE/BSE stocks for Fundamentals, Capital Allocation, and Integrity.")

# Sidebar for Input
with st.sidebar:
    st.header("Search Settings")
    market = st.radio("Select Exchange", ["NSE", "BSE"])
    suffix = ".NS" if market == "NSE" else ".BO"
    
    ticker_input = st.text_input("Enter Stock Ticker (e.g., RELIANCE, TCS, INFOTEL)", "RELIANCE")
    full_symbol = ticker_input.upper() + suffix

# Main Action
if st.button("Run Fundamental Analysis"):
    with st.spinner(f"Fetching data for {full_symbol}..."):
        stock = get_stock_info(full_symbol)
        
        try:
            info = stock.info
            
            # Display Header
            st.header(f"{info.get('longName', 'Company')} Analysis")
            st.write(info.get('longBusinessSummary', 'No summary available.'))
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Current Price", f"₹{info.get('currentPrice')}")
            col2.metric("P/E Ratio", f"{info.get('trailingPE', 'N/A')}")
            col3.metric("Market Cap", f"₹{info.get('marketCap', 0):,}")

            st.divider()

            # Fundamental Analysis Section
            tab1, tab2, tab3 = st.tabs(["📊 Key Stats", "💰 Capital Allocation", "🛡️ Management Integrity"])
            
            with tab1:
                st.subheader("Financial Overview")
                stats = {
                    "Metric": ["Price to Book", "Debt to Equity", "ROE", "Revenue Growth"],
                    "Value": [info.get('priceToBook'), info.get('debtToEquity'), info.get('returnOnEquity'), info.get('revenueGrowth')]
                }
                st.table(pd.DataFrame(stats))

            with tab2:
                st.subheader("Capital Allocation Analysis")
                st.info(analyze_capital_allocation(stock))

            with tab3:
                st.subheader("Management Integrity Check")
                st.write("Comparing Net Income to Operating Cash Flow to detect 'paper profits'.")
                st.warning(analyze_integrity(stock))

        except Exception as e:
            st.error(f"Could not find data for {full_symbol}. Ensure the ticker is correct for {market}.")
