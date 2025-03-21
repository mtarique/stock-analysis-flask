from flask import Flask, request, render_template, jsonify
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import time
import datetime

app = Flask(__name__)

def date_to_unix(date_string):
    # Convert the date string to a datetime object
    date_object = datetime.datetime.strptime(date_string, '%Y-%m-%d')
    
    # Convert the datetime object to a Unix timestamp
    unix_timestamp = int(time.mktime(date_object.timetuple()))
    
    return unix_timestamp

# Function to prepare data for modeling
def prepare_data(df):
    # Convert 'Close' to numeric, coercing errors (in case there are any non-numeric values)
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')

    df['Price Change'] = df['Close'].diff()
    df['Price Change %'] = (df['Price Change'] / df['Close'].shift(1)) * 100
    df['Target'] = df['Price Change %'].shift(-1)  # Predict the next day's change

    # Drop rows with NaN values
    df = df.dropna()

    return df[['Close', 'Price Change %', 'Target']]

# Function to predict stock performance
def predict_stock_performance(stock_data):
    X = stock_data[['Close', 'Price Change %']]
    y = stock_data['Target']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train a linear regression model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Predict on the test set
    predictions = model.predict(X_test)

    # Return predictions
    return predictions, y_test

# Function to decide which stock to buy
def decide_which_to_buy(predictions, actuals):
    results = pd.DataFrame({'Predicted': predictions, 'Actual': actuals})
    results['Recommendation'] = np.where(results['Predicted'] > 0, 'BUY', 'HOLD')
    return results

@app.route('/')
def index():
    # Render the main page with the form
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def stock_analysis():
    chart_html = None  # Initialize chart_html to None
    stock_data_table = None  # Initialize chart_html to None
    
    stock_symbol = request.json.get('symbol')
    period = request.json.get('period')
    # start_date = request.json.get('start_date')
    # end_date = request.json.get('end_date')

    # Get historical data for the stock symbol
    stock = yf.Ticker(stock_symbol)
    # stock_data = stock.history(start=start_date, end=end_date)
    stock_data = stock.history(period=period)

    if stock_data.empty:
        return jsonify({'error': "No data found for the given stock symbol and date range."})

    # Create a candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=stock_data.index,
        open=stock_data['Open'],
        high=stock_data['High'],
        low=stock_data['Low'],
        close=stock_data['Close']
    )])
    fig.update_layout(title=f'{stock_symbol} Stock Price', xaxis_title='Date', yaxis_title='Price')

    # Convert the chart to HTML
    candle_stick_chart = fig.to_html(full_html=False)

    # Create a line chart for closing prices
    price_line_fig = go.Figure()
    price_line_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'], mode='lines', name='Close Price', line=dict(color='green')))
    price_line_fig.update_layout(title=f'{stock_symbol} Closing Prices', xaxis_title='Date', yaxis_title='Price')

    # Convert the line chart for prices to HTML
    price_line_chart = price_line_fig.to_html(full_html=False)

    # Pass stock data as a table
    stock_data_table = stock_data.reset_index().to_dict('records')

    # Prepare the data
    prepared_data = prepare_data(stock_data)

    # Predict stock performance
    predictions, actuals = predict_stock_performance(prepared_data)

    # Decide which stocks to buy
    result = decide_which_to_buy(predictions, actuals)

    # Get the last prediction for today's decision
    recommendation = result.iloc[-1]['Recommendation']

    # Get the latest close price and previous close price
    latest_close = stock_data['Close'].iloc[-1]
   
    previous_close = stock_data['Close'].iloc[-2]
    close_datetime = stock_data.index[-1]

    price_change = latest_close - previous_close; 

    # Calculate the price change percentage
    price_change_pct = ((price_change) / previous_close) * 100

    # Create a moving average chart (50-day and 200-day) - KEEP THIS CODE AFTER ALL ABOVE CODE BECAUSE STOCK_DATA IS GETTING MODIFIED HERE
    stock_data['50_MA'] = stock_data['Close'].rolling(window=50).mean()
    stock_data['200_MA'] = stock_data['Close'].rolling(window=200).mean()

    ma_fig = go.Figure()
    ma_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['50_MA'], mode='lines', name='50-Day MA', line=dict(color='blue')))
    ma_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['200_MA'], mode='lines', name='200-Day MA', line=dict(color='red')))
    ma_fig.update_layout(title=f'{stock_symbol} Moving Averages (50 & 200-Day)', xaxis_title='Date', yaxis_title='Price')

    # Convert the moving average chart to HTML
    line_chart = ma_fig.to_html(full_html=False)

    return jsonify({'candle_stick_chart': candle_stick_chart, 'price_line_chart': price_line_chart, 'line_chart': line_chart, 'stock_data_table': stock_data_table, 'stock_info': stock.info, 'stock_news': stock.news, 'close_datetime': close_datetime, 'price_change': price_change, 'price_change_pct': price_change_pct, 'prediction': recommendation})

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5001, debug=True)
