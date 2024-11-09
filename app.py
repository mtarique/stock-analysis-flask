from flask import Flask, request, render_template, jsonify
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import time
import datetime

app = Flask(__name__)

def date_to_unix(date_string):
    # Convert the date string to a datetime object
    date_object = datetime.datetime.strptime(date_string, '%Y-%m-%d')
    
    # Convert the datetime object to a Unix timestamp
    unix_timestamp = int(time.mktime(date_object.timetuple()))
    
    return unix_timestamp

@app.route('/')
def index():
    # Render the main page with the form
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def stock_analysis():
    chart_html = None  # Initialize chart_html to None
    stock_data_table = None  # Initialize chart_html to None
    
    stock_symbol = request.json.get('symbol')
    start_date = request.json.get('start_date')
    end_date = request.json.get('end_date')

    # Get historical data for the stock symbol
    stock = yf.Ticker(stock_symbol)
    stock_data = stock.history(start=start_date, end=end_date)

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
    chart_html = fig.to_html(full_html=False)

    # Pass stock data as a table
    stock_data_table = stock_data.reset_index().to_dict('records')

    return jsonify({'chart_html': chart_html, 'stock_data_table': stock_data_table})

if __name__ == '__main__':
    app.run(debug=True)
