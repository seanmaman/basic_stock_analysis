import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from ta.momentum import RSIIndicator
import wikipedia
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="📈 Stock Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .header-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid #e0e6ed;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .stock-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
        margin: 1rem 0;
    }
    .positive {
        color: #00C851;
        font-weight: bold;
    }
    .negative {
        color: #ff4444;
        font-weight: bold;
    }
    .neutral {
        color: #ffbb33;
        font-weight: bold;
    }
    .feature-icons {
        font-size: 1.2rem;
        margin: 0 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def format_market_cap(value):
    """Format market cap with M/B/T suffixes"""
    if value is None or value == 0:
        return "N/A"
    
    if value >= 1_000_000_000_000:  # Trillions
        return f"${value / 1_000_000_000_000:.2f}T"
    elif value >= 1_000_000_000:  # Billions
        return f"${value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:  # Millions
        return f"${value / 1_000_000:.2f}M"
    else:
        return f"${value:,.0f}"

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_data(ticker, period="6mo"):
    """Get stock data matching the original script format"""
    try:
        tkr = yf.Ticker(ticker)
        info = tkr.info
        hist = tkr.history(period=period)
        
        if hist.empty:
            return None
            
        # Calculate 50-day moving average
        hist["MA50"] = hist["Close"].rolling(50).mean()
        
        # Calculate RSI
        rsi = RSIIndicator(hist["Close"], 14).rsi()
        
        # Return data in the exact format from original script
        return {
            "Ticker": ticker.upper(),
            "Price": info.get("currentPrice"),
            "P/E": info.get("trailingPE"),
            "Forward P/E": info.get("forwardPE"),
            "Price/Book": info.get("priceToBook"),
            "Market Cap": format_market_cap(info.get('marketCap', 0)),
            "Debt/Equity": info.get("debtToEquity"),
            "RSI": rsi.iloc[-1] if not rsi.isna().all() else None,
            "50-day MA": hist["MA50"].iloc[-1] if not hist["MA50"].isna().all() else None,
            "Beta": info.get("beta"),
            "Analyst Rating": info.get("recommendationKey"),
            "Target Price": info.get("targetMeanPrice"),
            "history": hist,
            "info": info
        }
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {str(e)}")
        return None

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_wikipedia_summary(ticker, sentences=3):
    """Get Wikipedia summary for the company with better search strategy"""
    try:
        info = yf.Ticker(ticker).info
        company_name = info.get("longName") or info.get("shortName")
    except Exception:
        company_name = None

    # Better search strategy - prioritize company-specific terms
    search_terms = []
    if company_name:
        # Add "Inc", "Corporation", "Company" to help disambiguate
        search_terms.extend([
            f"{company_name} Inc",
            f"{company_name} Corporation",
            f"{company_name} Company",
            company_name
        ])
    
    # Add ticker with "stock" or "company" to avoid confusion
    search_terms.extend([
        f"{ticker} stock",
        f"{ticker} company",
        f"{ticker} corporation",
        ticker
    ])

    for term in search_terms:
        try:
            return wikipedia.summary(term, sentences=sentences,
                                   auto_suggest=True, redirect=True)
        except wikipedia.exceptions.DisambiguationError as e:
            # Look for business-related options first
            business_keywords = ['inc', 'corp', 'company', 'corporation', 'ltd', 'technology', 'software', 'systems']
            for option in e.options:
                option_lower = option.lower()
                if any(keyword in option_lower for keyword in business_keywords):
                    try:
                        return wikipedia.summary(option, sentences=sentences,
                                               auto_suggest=False)
                    except Exception:
                        continue
            # If no business-related option found, try the first one
            if e.options:
                try:
                    return wikipedia.summary(e.options[0], sentences=sentences,
                                           auto_suggest=False)
                except Exception:
                    continue
        except wikipedia.exceptions.PageError:
            continue
        except Exception:
            continue

    return "Wikipedia summary not found."

def create_simple_price_chart(data):
    """Create a simple price trend chart"""
    hist = data["history"]
    ticker = data["Ticker"]
    
    fig = go.Figure()
    
    # Simple line chart for price trend
    fig.add_trace(
        go.Scatter(
            x=hist.index,
            y=hist['Close'],
            mode='lines',
            name=f'{ticker} Price',
            line=dict(color='#1f77b4', width=3),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Date: %{x}<br>' +
                         'Price: $%{y:.2f}<extra></extra>'
        )
    )
    
    # Add 50-day moving average if available
    if not hist["MA50"].isna().all():
        fig.add_trace(
            go.Scatter(
                x=hist.index,
                y=hist['MA50'],
                mode='lines',
                name='50-day MA',
                line=dict(color='orange', width=2, dash='dash'),
                hovertemplate='<b>50-day MA</b><br>' +
                             'Date: %{x}<br>' +
                             'MA: $%{y:.2f}<extra></extra>'
            )
        )
    
    fig.update_layout(
        title=f'{ticker} - Price Trend',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        height=400,
        showlegend=True,
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig

def create_comparison_chart(all_data):
    """Create a simple comparison chart for multiple stocks"""
    if len(all_data) < 2:
        return None
    
    fig = go.Figure()
    
    for data in all_data:
        hist = data["history"]
        ticker = data["Ticker"]
        
        # Normalize prices to percentage change from first day
        normalized_prices = (hist['Close'] / hist['Close'].iloc[0] - 1) * 100
        
        fig.add_trace(
            go.Scatter(
                x=hist.index,
                y=normalized_prices,
                mode='lines',
                name=ticker,
                line=dict(width=3),
                hovertemplate=f'<b>{ticker}</b><br>' +
                             'Date: %{x}<br>' +
                             'Change: %{y:.2f}%<extra></extra>'
            )
        )
    
    fig.update_layout(
        title='Stock Price Comparison (% Change)',
        xaxis_title='Date',
        yaxis_title='Price Change (%)',
        height=500,
        showlegend=True,
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig

def build_dashboard(tickers, period="6mo"):
    """Build dashboard for multiple tickers (up to 10)"""
    # Handle single ticker input
    if isinstance(tickers, str):
        tickers = [tickers]
    
    # Limit to 10 stocks maximum
    if len(tickers) > 10:
        st.warning(f"Only analyzing first 10 stocks out of {len(tickers)} provided.")
        tickers = tickers[:10]
    
    # Collect data for all tickers
    all_data = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, ticker in enumerate(tickers):
        status_text.text(f"Fetching data for {ticker.strip().upper()}...")
        progress_bar.progress((i + 1) / len(tickers))
        
        try:
            stock_data = get_stock_data(ticker.strip().upper(), period)
            if stock_data:
                all_data.append(stock_data)
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    if not all_data:
        st.error("No valid stock data found.")
        return pd.DataFrame()
    
    # Create DataFrame with all metrics (matching original script)
    fundamentals_data = []
    for data in all_data:
        fundamentals_data.append({
            "Ticker": data["Ticker"],
            "Price": data["Price"],
            "P/E": data["P/E"],
            "Forward P/E": data["Forward P/E"],
            "Price/Book": data["Price/Book"],
            "Market Cap": data["Market Cap"],
            "Debt/Equity": data["Debt/Equity"],
            "RSI": data["RSI"],
            "50-day MA": data["50-day MA"],
            "Beta": data["Beta"],
            "Analyst Rating": data["Analyst Rating"],
            "Target Price": data["Target Price"]
        })
    
    fundamentals = pd.DataFrame(fundamentals_data)
    
    return fundamentals, all_data

def main():
    # Enhanced Header with visual elements
    st.markdown("""
    <div class="header-container">
        <div style="text-align: center;">
            <div style="font-size: 5rem; margin-bottom: 1rem; background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57); background-size: 300% 300%; animation: gradient 3s ease infinite;">
                📊📈💹🚀💰
            </div>
            <h1 class="main-header">Stock Analysis Dashboard</h1>
            <div style="font-size: 1.3rem; color: #555; margin-top: 1.5rem; font-weight: 500;">
                <span class="feature-icons">🎯</span>Simple stock analysis with price trends and comprehensive metrics<span class="feature-icons">📊</span>
            </div>
            <div style="margin-top: 1.5rem; font-size: 1rem; color: #777; display: flex; justify-content: center; flex-wrap: wrap; gap: 2rem;">
                <span><strong>✨ Real-time Data</strong></span>
                <span><strong>📚 Educational Explanations</strong></span>
                <span><strong>💾 CSV Exports</strong></span>
                <span><strong>📈 Up to 10 Stocks</strong></span>
            </div>
        </div>
    </div>
    
    <style>
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Stock input
        st.subheader("📊 Stock Selection")
        ticker_input = st.text_input(
            "Enter stock tickers (comma-separated)",
            value="AAPL,MSFT,GOOGL",
            help="Enter up to 10 stock symbols separated by commas (e.g., AAPL,MSFT,GOOGL,TSLA,AMZN)"
        )
        
        # Time period selection
        period = st.selectbox(
            "Select time period",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=2,
            help="Choose the historical data period"
        )
        
        # Analysis button
        analyze_button = st.button("🚀 Analyze Stocks", type="primary", use_container_width=True)
        
        st.markdown("---")
        st.subheader("ℹ️ About")
        st.info(
            "This dashboard provides:\n"
            "• Simple price trend charts\n"
            "• Key financial metrics\n"
            "• CSV export functionality\n"
            "• Support for up to 10 stocks\n"
            "• Company information"
        )
    
    # Main content
    if analyze_button or ticker_input:
        # Parse tickers
        tickers = [ticker.strip().upper() for ticker in ticker_input.split(",") if ticker.strip()]
        
        if not tickers:
            st.error("Please enter at least one valid stock ticker.")
            return
        
        # Build dashboard
        fundamentals, all_data = build_dashboard(tickers, period)
        
        if fundamentals.empty:
            st.error("No valid stock data found. Please check your ticker symbols.")
            return
        
        # Display results
        st.success(f"Successfully analyzed {len(all_data)} stocks!")
        
        # Key Metrics Table
        st.header("📊 Key Metrics Summary")
        st.dataframe(fundamentals, use_container_width=True)
        
        # Add comprehensive explanations for ALL metrics
        with st.expander("📚 Complete Guide to All Stock Metrics"):
            st.markdown("### 🎓 Understanding Every Number in the Table")
            
            # Create tabs for different categories
            tab1, tab2, tab3, tab4 = st.tabs(["💰 Valuation", "📈 Technical", "🏢 Health", "🎯 Analyst"])
            
            with tab1:
                st.markdown("""
                ### 💰 Valuation Metrics - "Is this stock expensive or cheap?"
                
                **💵 Price:**
                - **What it is:** Current cost to buy one share
                - **How to use:** Compare with historical prices
                - **Example:** Apple at $150 = you pay $150 for one share
                
                **📊 P/E Ratio (Price-to-Earnings):**
                - **What it is:** How much you pay for each dollar of profit
                - **Formula:** Stock Price ÷ Annual Earnings per Share
                - **Low P/E (5-15):** Cheap stock or troubled company
                - **Medium P/E (15-25):** Fairly valued
                - **High P/E (25+):** Expensive, high growth expected
                - **Example:** P/E of 20 = pay $20 for every $1 of annual profit
                
                **🔮 Forward P/E:**
                - **What it is:** P/E based on expected future earnings
                - **Why important:** Shows future value expectations
                - **Lower than current P/E:** Growing earnings expected
                
                **📖 Price/Book:**
                - **What it is:** Price vs company's asset value
                - **Below 1:** Trading below asset value (potential bargain)
                - **1-3:** Normal range
                - **Above 3:** Premium valuation
                """)
            
            with tab2:
                st.markdown("""
                ### 📈 Technical Indicators - "What's the momentum?"
                
                **🎯 RSI (0-100 scale):**
                - **What it is:** Momentum meter for stocks
                - **0-30:** Oversold (might bounce up)
                - **30-70:** Normal range
                - **70-100:** Overbought (might drop)
                - **Example:** RSI 80 = rising very fast lately
                
                **📊 50-day Moving Average:**
                - **What it is:** Average price over 50 days
                - **Purpose:** Shows real trend, ignores daily noise
                - **Price above MA:** Upward trend
                - **Price below MA:** Downward trend
                
                **⚡ Beta:**
                - **What it is:** Volatility vs market
                - **Beta < 1:** Less volatile (safer)
                - **Beta = 1:** Moves with market
                - **Beta > 1:** More volatile (riskier)
                - **Example:** Beta 1.5 = if market +10%, stock typically +15%
                """)
            
            with tab3:
                st.markdown("""
                ### 🏢 Company Health - "How strong is the company?"
                
                **🏦 Market Cap:**
                - **What it is:** Total company value
                - **Small Cap:** Under $2B (risky, high potential)
                - **Mid Cap:** $2-10B (balanced)
                - **Large Cap:** Over $10B (stable)
                
                **💳 Debt/Equity:**
                - **What it is:** How much debt vs equity
                - **Low (0-0.3):** Conservative, safe
                - **Medium (0.3-0.6):** Balanced
                - **High (0.6+):** Aggressive, risky
                """)
            
            with tab4:
                st.markdown("""
                ### 🎯 Analyst Data - "What do experts think?"
                
                **⭐ Analyst Rating:**
                - **Strong Buy:** Very bullish
                - **Buy:** Positive outlook
                - **Hold:** Neutral
                - **Sell:** Negative outlook
                
                **🎯 Target Price:**
                - **What it is:** Expected price in 12 months
                - **Target > Current:** Expected to rise
                - **Target < Current:** Expected to fall
                - **Note:** Predictions, not guarantees!
                """)
        
        # CSV Download
        st.header("💾 Download Data")
        col1, col2 = st.columns(2)
        
        with col1:
            csv = fundamentals.to_csv(index=False)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ticker_str = "_".join([ticker.strip().upper() for ticker in tickers])
            filename = f"stock_analysis_{ticker_str}_{timestamp}.csv"
            
            st.download_button(
                label="📥 Download Metrics CSV",
                data=csv,
                file_name=filename,
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            if len(all_data) > 0:
                # Combine historical data for download
                combined_hist = pd.DataFrame()
                for data in all_data:
                    hist_copy = data["history"].copy()
                    hist_copy['Ticker'] = data["Ticker"]
                    combined_hist = pd.concat([combined_hist, hist_copy])
                
                hist_csv = combined_hist.to_csv()
                hist_filename = f"historical_data_{ticker_str}_{timestamp}.csv"
                
                st.download_button(
                    label="📊 Download Historical CSV",
                    data=hist_csv,
                    file_name=hist_filename,
                    mime="text/csv",
                    use_container_width=True
                )
        
        # Price Trend Charts
        st.header("📈 Price Trends")
        
        # Comparison chart for multiple stocks
        if len(all_data) > 1:
            st.subheader("Stock Comparison (% Change)")
            comparison_chart = create_comparison_chart(all_data)
            if comparison_chart:
                st.plotly_chart(comparison_chart, use_container_width=True)
        
        # Individual stock charts
        st.subheader("Individual Stock Trends")
        
        if len(all_data) == 1:
            # Single stock - show directly
            price_chart = create_simple_price_chart(all_data[0])
            st.plotly_chart(price_chart, use_container_width=True)
        else:
            # Multiple stocks - use columns for better layout
            cols_per_row = 2
            for i in range(0, len(all_data), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, data in enumerate(all_data[i:i+cols_per_row]):
                    with cols[j]:
                        price_chart = create_simple_price_chart(data)
                        st.plotly_chart(price_chart, use_container_width=True)
        
        # Technical Indicators Summary
        st.header("📊 Technical Indicators Summary")
        st.markdown("*Here's what the numbers mean for each stock:*")
        
        for data in all_data:
            with st.expander(f"📈 {data['Ticker']} - What Do The Numbers Tell Us?"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # RSI Analysis with detailed explanation
                    rsi_value = data['RSI']
                    if rsi_value:
                        st.metric("RSI (Momentum Meter)", f"{rsi_value:.1f}/100")
                        
                        if rsi_value > 70:
                            st.warning("⚠️ **Stock is HOT (Overbought)**")
                            st.write(f"**What this means:** {data['Ticker']} has been rising very fast recently. The RSI of {rsi_value:.1f} suggests it might be 'too expensive' right now and could drop a bit soon.")
                            st.write("**Think of it like:** A stock that's been on a winning streak - might need a break!")
                        elif rsi_value < 30:
                            st.success("✅ **Stock is COOL (Oversold)**")
                            st.write(f"**What this means:** {data['Ticker']} has been falling recently. The RSI of {rsi_value:.1f} suggests it might be 'too cheap' right now and could bounce back up.")
                            st.write("**Think of it like:** A good stock that's on sale - might be a buying opportunity!")
                        else:
                            st.info("ℹ️ **Stock is BALANCED (Normal)**")
                            st.write(f"**What this means:** {data['Ticker']} is trading normally. The RSI of {rsi_value:.1f} shows no extreme buying or selling pressure.")
                            st.write("**Think of it like:** A stock that's cruising at a steady pace - no drama!")
                    else:
                        st.metric("RSI (Momentum Meter)", "N/A")
                        st.info("Not enough data to calculate RSI for this stock")
                
                with col2:
                    # Moving Average Analysis with detailed explanation
                    ma_value = data['50-day MA']
                    current_price = data['Price']
                    if ma_value and current_price:
                        st.metric("50-day Average Price", f"${ma_value:.2f}")
                        st.metric("Current Price", f"${current_price:.2f}")
                        
                        price_vs_ma = ((current_price - ma_value) / ma_value) * 100
                        if current_price > ma_value:
                            st.success("✅ **UPWARD TREND (Bullish)**")
                            st.write(f"**Current Price:** ${current_price:.2f}")
                            st.write(f"**50-day Average:** ${ma_value:.2f}")
                            st.write(f"**Difference:** {price_vs_ma:.1f}% ABOVE the average")
                            st.write("**What this means:** The stock is trading above its recent average price, showing an upward trend.")
                            st.write("**Think of it like:** The stock is climbing uphill - it's been doing better than usual!")
                        else:
                            st.warning("⚠️ **DOWNWARD TREND (Bearish)**")
                            st.write(f"**Current Price:** ${current_price:.2f}")
                            st.write(f"**50-day Average:** ${ma_value:.2f}")
                            st.write(f"**Difference:** {abs(price_vs_ma):.1f}% BELOW the average")
                            st.write("**What this means:** The stock is trading below its recent average price, showing a downward trend.")
                            st.write("**Think of it like:** The stock is going downhill - it's been struggling lately.")
                    else:
                        st.metric("50-day Average Price", "N/A")
                        st.info("Not enough data to calculate moving average for this stock")

        # Company Information
        st.header("🏢 Company Information")
        
        if len(all_data) == 1:
            # Single stock - show directly
            wiki_summary = get_wikipedia_summary(all_data[0]["Ticker"])
            st.write(f"**{all_data[0]['Ticker']}:** {wiki_summary}")
        else:
            # Multiple stocks - use expanders
            for data in all_data:
                with st.expander(f"📋 {data['Ticker']} - Company Info"):
                    wiki_summary = get_wikipedia_summary(data["Ticker"])
                    st.write(wiki_summary)
                    
                    # Show key metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Current Price", f"${data['Price']:.2f}" if data['Price'] else "N/A")
                    with col2:
                        st.metric("P/E Ratio", f"{data['P/E']:.2f}" if data['P/E'] else "N/A")
                    with col3:
                        st.metric("Market Cap", data['Market Cap'] if data['Market Cap'] else "N/A")

if __name__ == "__main__":
    main()