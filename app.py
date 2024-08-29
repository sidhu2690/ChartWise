from flask import Flask, render_template, request, redirect, url_for
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)

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

def get_stock_data():
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
            gain_loss = ((current_price - suggested_price) / suggested_price) * 100
            rsi = calculate_rsi(history)
            short_ma = calculate_moving_average(history, 20)
            long_ma = calculate_moving_average(history, 50)
            macd, signal_line = calculate_macd(history)
            upper_band, lower_band = calculate_bollinger_bands(history)
            
            # Calculate daily change percentage
            daily_change = ((current_price - history['Close'].iloc[-2]) / history['Close'].iloc[-2]) * 100
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
            'Suggested Price': suggested_price,
            'Current Price': current_price,
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

@app.route('/', methods=['GET', 'POST'])
def index():
    global stocks
    if request.method == 'POST':
        symbol = request.form['symbol']
        suggested_price = float(request.form['suggested_price'])
        stocks.append({'symbol': symbol, 'suggested_price': suggested_price})
        save_stocks(stocks)
        return redirect(url_for('index'))
    
    stock_data, top_gainers, top_losers = get_stock_data()
    
    # Handle sorting
    sort_column = request.args.get('sort', 'Stock Symbol')
    sort_order = request.args.get('order', 'asc')
    reverse = True if sort_order == 'desc' else False
    stock_data = sorted(stock_data, key=lambda x: x.get(sort_column, 0) or 0, reverse=reverse)
    
    return render_template('index.html', stock_data=stock_data, top_gainers=top_gainers, top_losers=top_losers, sort_column=sort_column, sort_order=sort_order)

if __name__ == '__main__':
    app.run(debug=True)
