from flask import Flask, request, render_template, redirect
import requests
import json
import pandas as pd
from bokeh.plotting import figure
from bokeh.io import output_file, save
from bokeh.embed import components
import os

def get_quandl(ticker):
    r = requests.get('https://www.quandl.com/api/v3/datasets/WIKI/'+ticker+'.json?api_key=ts2seF_Hy53zE-K6xcxz')
    
    if r.status_code != 404:
        # extract stock data
        data = json.loads(r.text)
        df = pd.DataFrame(data['dataset']['data'])
        # assign column names
        df.columns = data['dataset']['column_names']
        # convert to datetime
        df['Date'] = pd.to_datetime(df['Date'])

        # return the last 30-days stock data
        df = df.head(30)

        # extract company name
        name = data['dataset']['name'].split('(')[0]

    else:
        print "Invalid stock ticker"
        df = None
        name = None
    return df, name


def plot_stock(df, features, ticker):
    p = figure(x_axis_type = 'datetime')
    # Color dictionary
    colors={'Open':'blue','Close':'green', 'High':'red'}
    # plot'open/high/close prices'
    for feature in features:
        p.line(df['Date'], df[feature], color = colors[feature], legend = feature)

    p.title = "Stock price of " +ticker+" for the last 30 days"
    p.grid.grid_line_alpha = 1.0
    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "Price"

    output_file('templates/stockplot.html', title=ticker+' stock price')
    save(p)
    return p


app = Flask(__name__)

@app.route('/')
def main():
    return redirect('/index')

@app.route('/index', methods = ['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/plot_stock', methods=['POST'])
def show_stock():
    # get the ticker input from the user
    ticker = request.form['ticker'].upper()

    # get list of checked features
    features = request.form.getlist('feature')

    # fetch data via Quandl
    df, name = get_quandl(ticker)
    # create Bokeh plot
    p = plot_stock(df, features, ticker)
    script, div = components(p)
    return render_template('stockplot.html', script = script, div = div, ticker = name)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug = True)
