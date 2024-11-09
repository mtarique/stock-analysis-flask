from flask import Flask, request, render_template
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

@app.route('/', methods=['GET', 'POST'])
def stock_analysis():
    chart_html = None  # Initialize chart_html to None
    stock_data_table = None  # Initialize chart_html to None
    if request.method == 'POST':
        stock_symbol = request.form['symbol']
        start_date = date_to_unix(request.form['start_date'])
        end_date = date_to_unix(request.form['end_date'])

        # Get historical data for TCS.NS
        stock = yf.Ticker(stock_symbol)
        
        # stock_data = stock.history(period="1y")
        stock_data = stock.history(start=start_date, end=end_date)

        # print("Stock data start")
        # stock_info = stock.info
        # current_price = stock_info.get('currentPrice')
        # print(current_price)
        # print("Stock data end")

        # Fetch historical data using yfinance
        # stock_data = yf.download(stock_symbol, start=start_date, end=end_date)

        if stock_data.empty:
            return render_template('index.html', error="No data found for the given stock symbol and date range.")

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

        # Pass stock data to the template as a table
        stock_data_table = stock_data.reset_index().to_dict('records')

    return render_template('index.html', chart_html=chart_html, stock_data_table=stock_data_table)

if __name__ == '__main__':

    app.run(debug=True)
