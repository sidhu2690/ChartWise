import streamlit as st
import yfinance as yf
import pandas as pd
import os

CSV_FILE = 'stocks.csv'

# Function to load stocks from CSV file
def load_stocks():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        return df.to_dict('records')
    return []

# Function to save stocks to CSV file
def save_stocks(stocks):
    df = pd.DataFrame(stocks)
    df.to_csv(CSV_FILE, index=False)

# Load stocks from file on startup
stocks = load_stocks()

def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_moving_average(data, window):
    return data['Close'].rolling(window=window).mean().iloc[-1]

def calculate_macd(data):
    ema_12 = data['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    signal_line = macd.ewm(span=9, adjust=False).mean()
    return macd.iloc[-1], signal_line.iloc[-1]

def calculate_bollinger_bands(data, window=20):
    sma = data['Close'].rolling(window=window).mean().iloc[-1]
    std_dev = data['Close'].rolling(window=window).std().iloc[-1]
    upper_band = sma + (std_dev * 2)
    lower_band = sma - (std_dev * 2)
    return upper_band, lower_band

def get_stock_data(stocks):
    data = []
    daily_changes = []

    for stock in stocks:
        symbol = stock['symbol']
        suggested_price = stock['suggested_price']
        ticker = yf.Ticker(symbol)
        
        history = ticker.history(period='6mo')
        current_price = history['Close'].iloc[-1] if not history.empty else None
        volume = history['Volume'].iloc[-1] if not history.empty else None
        avg_volume = history['Volume'].mean() if not history.empty else None
        market_cap = ticker.info.get('marketCap', 'N/A')
        
        if current_price is not None:
            gain_loss = round(((current_price - suggested_price) / suggested_price) * 100, 2)
            rsi = round(calculate_rsi(history), 2)
            short_ma = round(calculate_moving_average(history, 20), 2)
            long_ma = round(calculate_moving_average(history, 50), 2)
            macd, signal_line = calculate_macd(history)
            macd = round(macd, 2)
            signal_line = round(signal_line, 2)
            upper_band, lower_band = calculate_bollinger_bands(history)
            upper_band = round(upper_band, 2)
            lower_band = round(lower_band, 2)
            
            # Calculate daily change percentage
            daily_change = round(((current_price - history['Close'].iloc[-2]) / history['Close'].iloc[-2]) * 100, 2)
            daily_changes.append((symbol, current_price, daily_change))
        else:
            gain_loss = None
            rsi = None
            short_ma = None
            long_ma = None
            macd = None
            signal_line = None
            upper_band = None
            lower_band = None
        
        data.append({
            'Stock Symbol': symbol,
            'Suggested Price': round(suggested_price, 2),
            'Current Price': round(current_price, 2) if current_price is not None else None,
            'Gain/Loss (%)': gain_loss,
            'RSI': rsi,
            'Short MA': short_ma,
            'Long MA': long_ma,
            'MACD': macd,
            'Signal Line': signal_line,
            'Upper Bollinger Band': upper_band,
            'Lower Bollinger Band': lower_band,
            'Volume': volume,
            'Average Volume': avg_volume,
            'Market Cap': market_cap
        })
    
    # Sort daily changes for top gainers and losers
    daily_changes_sorted = sorted(daily_changes, key=lambda x: x[2], reverse=True)
    top_gainers = daily_changes_sorted[:10]
    top_losers = daily_changes_sorted[-10:]
    
    return data, top_gainers, top_losers

def get_indices_data():
    symbols = {
        'Nifty 50': '^NSEI',
        'Sensex': '^BSESN',
        'India VIX': '^INDIAVIX',
        'Bank Nifty': '^NSEBANK',
        'Nifty Midcap 50': '^NSEMDCP50',
        'Nifty IT': '^CNXIT',
        'Nifty Pharma': '^CNXPHARMA',
        'Nifty FMCG': '^CNXFMCG',
        'Nifty Energy': '^CNXENERGY',
        'Nifty Auto': '^CNXAUTO',
        'USD/INR Exchange Rate': 'INR=X',
        'Crude Oil Prices': 'CL=F',
        'Gold Prices': 'GC=F',
        'S&P 500': '^GSPC',
        'Dow Jones Industrial Average': '^DJI',
        'NASDAQ Composite': '^IXIC'
    }
    
    data = {}
    for name, symbol in symbols.items():
        ticker = yf.Ticker(symbol)
        history = ticker.history(period='1d')
        current_price = history['Close'].iloc[-1] if not history.empty else 'N/A'
        data[name] = {
            'Current Price': round(current_price, 2) if current_price != 'N/A' else current_price
        }
    
    return data

def main():
    st.title('Stock Tracker')

    # User input to add new stock
    symbol = st.text_input('Stock Symbol', '')
    suggested_price = st.number_input('Suggested Price', min_value=0.0, step=0.01)
    if st.button('Add Stock'):
        stocks.append({'symbol': symbol, 'suggested_price': suggested_price})
        save_stocks(stocks)
        st.success(f'Stock {symbol} added.')

    # Display stock data
    stock_data, top_gainers, top_losers = get_stock_data(stocks)
    current_market_data = get_indices_data()
    
    # Sorting options
    sort_column = st.selectbox('Sort By', ['Stock Symbol', 'Gain/Loss (%)', 'RSI', 'Current Price'])
    sort_order = st.radio('Sort Order', ['Ascending', 'Descending'])
    reverse = True if sort_order == 'Descending' else False
    stock_data = sorted(stock_data, key=lambda x: x.get(sort_column, 0) or 0, reverse=reverse)

    # Display stock data table
    st.write('### Stock Data')
    st.table(stock_data)
    
    # Display top gainers and losers
    st.write('### Top 10 Gainers')
    st.table(top_gainers)

    st.write('### Top 10 Losers')
    st.table(top_losers)

    # Display market indices data
    st.write('### Market Indices')
    st.table(current_market_data)

if __name__ == '__main__':
    main()
