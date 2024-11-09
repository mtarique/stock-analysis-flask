from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
import time
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, MonthLocator, YearLocator, DayLocator
import plotly.graph_objects as go
import seaborn as sns
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

# Convert date string to Unix timestamp
def date_to_unix(date_string):
    date_object = datetime.datetime.strptime(date_string, '%Y-%m-%d')
    unix_timestamp = int(time.mktime(date_object.timetuple()))
    return unix_timestamp

# Function to get stock historical data
def get_stock_historical_data(ticker, start_date, end_date):
    period1 = date_to_unix(start_date)
    period2 = date_to_unix(end_date)
    url = f'https://finance.yahoo.com/quote/{ticker}/history?period1={period1}&period2={period2}'
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'W(100%) M(0)'})

    if not table:
        return None

    headers = [header.get_text() for header in table.find('thead').find_all('th')]
    rows = []
    for row in table.find('tbody').find_all('tr'):
        cols = [col.get_text() for col in row.find_all('td')]
        if cols:
            rows.append(cols)
    df = pd.DataFrame(rows, columns=headers)
    return df

# Flask route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        stock_symbol = request.form['stock_symbol']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        return redirect(url_for('stock_history', stock_symbol=stock_symbol, start_date=start_date, end_date=end_date))
    return render_template('index.html')

# Flask route to display stock history
@app.route('/history')
def stock_history():
    stock_symbol = request.args.get('stock_symbol')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    df = get_stock_historical_data(stock_symbol, start_date, end_date)
    if df is None:
        return "Error: Could not retrieve data. Please check the stock symbol or date range."

    csv_filename = f"stock_data_{stock_symbol}.csv"
    df.to_csv(csv_filename, index=False)

    # Basic analysis (can be expanded as needed)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'])])
    fig.update_layout(title=f'{stock_symbol} Stock Price Candlestick Chart',
                      xaxis_title='Date',
                      yaxis_title='Price')
    fig.show()

    return f"Data has been processed and saved as {csv_filename}."

if __name__ == '__main__':
    app.run(debug=True)
