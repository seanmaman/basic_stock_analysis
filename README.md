[README.md](https://github.com/user-attachments/files/21619171/README.md)
# 📈 Stock Analysis Dashboard

A comprehensive Streamlit application that transforms stock analysis into beautiful, interactive visualizations and reports.

## 🌟 Features

- **Real-time Stock Data**: Fetch live stock prices and information using Yahoo Finance
- **Interactive Charts**: Beautiful candlestick charts with technical indicators
- **Technical Analysis**: RSI, Moving Averages, Bollinger Bands, and more
- **Multi-Stock Comparison**: Compare up to 5 stocks side by side
- **Company Information**: Wikipedia summaries and key metrics
- **Export Functionality**: Download data as CSV files
- **Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Start

### Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run streamlit_stock_app.py
```

The app will open in your default web browser at `http://localhost:8501`

## 📊 How to Use

1. **Enter Stock Tickers**: In the sidebar, enter stock symbols separated by commas (e.g., `AAPL,MSFT,GOOGL`)
2. **Select Time Period**: Choose the historical data period (1 month to 2 years)
3. **Click Analyze**: Hit the "🚀 Analyze Stocks" button to generate the report
4. **Explore Results**: 
   - View comparison charts for multiple stocks
   - Dive into detailed analysis for each stock
   - Download data as CSV files

## 📈 What You'll Get

### For Each Stock:
- **Current Price & Metrics**: Real-time price, P/E ratio, market cap, RSI, Beta
- **Technical Analysis**: Moving average trends, RSI signals, volume analysis
- **Interactive Charts**: Candlestick charts with technical indicators including:
  - 20-day and 50-day Moving Averages
  - Bollinger Bands
  - RSI (Relative Strength Index)
  - Volume with moving average
- **Valuation Metrics**: Forward P/E, Price/Book, Debt/Equity ratios
- **Analyst Information**: Recommendations and target prices
- **Performance Metrics**: 1-month and 3-month returns
- **Company Info**: Wikipedia summary and business description

### For Multiple Stocks:
- **Comparison Dashboard**: Side-by-side comparison of key metrics
- **Summary Table**: All important data in one view
- **Individual Tabs**: Detailed analysis for each stock

## 🛠️ Technical Indicators Explained

- **RSI (Relative Strength Index)**: Measures overbought/oversold conditions
  - Above 70: Potentially overbought
  - Below 30: Potentially oversold
- **Moving Averages**: Trend indicators
  - MA20 > MA50: Bullish trend
  - MA20 < MA50: Bearish trend
- **Bollinger Bands**: Volatility indicators showing price channels
- **Volume Analysis**: Trading activity compared to historical averages

## 📁 File Structure

```
├── streamlit_stock_app.py    # Main Streamlit application
├── stock_retriver.py         # Original stock analysis script
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── draft/                   # Draft files and experiments
```

## 🔧 Dependencies

- **streamlit**: Web app framework
- **yfinance**: Yahoo Finance data
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **plotly**: Interactive charts
- **ta**: Technical analysis indicators
- **wikipedia**: Company information

## 🎨 Features Highlights

### Beautiful Visualizations
- Interactive candlestick charts
- Technical indicator overlays
- Responsive design with custom CSS
- Color-coded signals (green/red/yellow)

### Smart Analysis
- Automatic trend detection
- Signal interpretation
- Risk assessment through Beta
- Volume trend analysis

### User-Friendly Interface
- Clean, intuitive design
- Progress indicators
- Error handling
- Mobile-responsive layout

## 🚨 Important Notes

- Data is fetched in real-time from Yahoo Finance
- Results are cached for 5-10 minutes for better performance
- Maximum of 5 stocks can be analyzed simultaneously
- Some data might not be available for all stocks
- This is for educational purposes only - not financial advice

## 🔄 Comparison with Original Script

The original `stock_retriver.py` provided basic analysis in text format. This Streamlit app enhances it with:

- **Visual Interface**: No more command-line interaction
- **Interactive Charts**: Beautiful, zoomable, interactive visualizations
- **Real-time Updates**: Live data with caching
- **Multiple Stocks**: Compare several stocks at once
- **Export Options**: Download data in various formats
- **Enhanced Analysis**: More technical indicators and metrics
- **Better UX**: Progress bars, error handling, responsive design

## 🤝 Contributing

Feel free to fork this project and submit pull requests for improvements!

## 📄 License

This project is open source and available under the MIT License.
