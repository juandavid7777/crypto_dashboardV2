import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import requests
import os

import scipy.stats as st
from scipy.stats import norm
import matplotlib.dates as dates
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn import metrics
from datetime import date, timedelta
import datetime

import streamlit as strl

from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics, svm



def bullet_fig_metric(value_in,
                      previous_val,
                      title_text,
                      ranges,
                      color_ranges = ["greenyellow", "lemonchiffon", "sandybrown", "lightcoral"],
                      color_comments = ["green", "gold", "darkorange", "red"],
                      format_num = ".2f",
                      log_scale = False):
  
    #Data preprocessing
    
      #Adds middle range
    ranges.insert(2, (ranges[1]+ranges[2])/2)
    
     #Changes format for axis
    format_string = '{:' + format_num + '}'
    ranges_labels = [format_string.format(item) for item in ranges]
    
      #Defines input chart values
    if log_scale == False:
        bar_value = value_in
        marker_value = bar_value
        ranges_plot = ranges

    else:
        bar_value = np.log10(value_in)
        marker_value = np.log10(value_in)
        ranges_plot = np.log10(ranges).tolist() 

      #Comments generation
    if value_in <= ranges[1]:
        comment = "Bottom"
        comment_color = color_comments[0]

    elif (value_in <= ranges[2]) & (value_in > ranges[1]):
        comment = "Mid Bottom"
        comment_color = color_comments[1]

    elif (value_in <= ranges[3]) & (value_in > ranges[2]):
        comment = "Mid top"
        comment_color = color_comments[2]

    else:
        comment = "Peaking"
        comment_color = color_comments[3]

    #Plots bullet figure
    fig = go.Figure(go.Indicator(
        mode = "number+gauge+delta",
        value = value_in,
        number = {'valueformat':format_num , "font": {"size" : 15 }},
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text' :"<b>" + title_text + "</b><br><span style='color: " + comment_color + "; font-size:0.7em'>" + comment + "</span>",
                  "font": {"size" : 15 }},
        delta = {'reference': previous_val, "relative" : False, 'valueformat':format_num},
        gauge = {
            'shape': "bullet",
            'axis': {"range": [ranges_plot[0], ranges_plot[-1]],
                     "tickmode":"array",
                     "tickvals":ranges_plot,
                     "ticktext": ranges_labels,
                     "tickformat":format_num,
                     "tickangle":90},      
            'threshold': {
                'line': {'color': "mediumblue", 'width': 3},
                'thickness': 0.9,
                'value': marker_value},
            'steps': [
                {'range': [ranges_plot[0], ranges_plot[1]], 'color': color_ranges[0]},
                {'range': [ranges_plot[1], ranges_plot[2]], 'color': color_ranges[1]},
                {'range': [ranges_plot[2], ranges_plot[3]], 'color': color_ranges[2]},
                {'range': [ranges_plot[3], ranges_plot[4]], 'color': color_ranges[3]}
            ],
            'bar':{'color':'black',
                  "thickness":0}
            }))

    fig.update_layout(
        margin=dict(l=130, r=30, t=15, b=70),
        height = 120,
        width = 500
    )

    return fig
    
    
@strl.cache_data   
def api_gn_bullet_data(metric, api_ID):

    #URL required for metric
    filename_metric = metric
    url = api_ID #source of info for price

    #Parameters required for metric
    api_key = strl.secrets["API_TOKEN"]
    a = "BTC"    #token
    s = '2020-01-01' #start date - not mandatory
    u = '2021-01-01' #until date - not mandatory
    i = '24h'         #time step
    f = "CSV"        #output format 
    timestamp_format = "humanized" #time stamp format

    #Compiles parameters
    params = (("a", a),("i", i),("f", f),("timestamp_format",timestamp_format ),("api_key", api_key))

    #Generates data requests and extracts the content
    r = requests.get(url, params)
    r_content = r.content

    #Writes the CSV temporary file
    csv_file = open(filename_metric+'.csv', 'wb')
    csv_file.write(r_content)
    csv_file.close()

    #Reads dataframe from temp file
    df = pd.read_csv(filename_metric+'.csv', parse_dates = [0], dayfirst = True)
    
    #Deletes file
    os.remove(filename_metric+'.csv')
    
    #Gets the results
    days_prev = 90
    
    val = df.value.iloc[-1]
    prev_val = df.value.iloc[-days_prev]
    min_val = df.value.min()
    max_val = df.value.max()

    return val, prev_val, min_val, max_val
    
@strl.cache_data    
def api_fg_bullet_data(metric, api_ID):
    
    #URL required for metric
    filename_metric = metric
    url = api_ID #source of info for price
    
    #Generates data requests and extracts the content
    r = requests.get(url)
    r_content = r.content

    #Writes the CSV file
    csv_file = open(filename_metric+'.csv', 'wb')
    csv_file.write(r_content)
    csv_file.close()

    #Cleans an formats database
        #Slices correct data
    df_fg = pd.read_csv(filename_metric+'.csv', header = 3)
    os.remove(filename_metric+'.csv')
    df_fg = df_fg.iloc[:-5]

        #Renames data
    df_fg = df_fg.rename(columns={"fng_value": "Date", "fng_classification": "fg", "date":"fg_cat"})

        #Sets Date as index
    df_fg['Date']= pd.to_datetime(df_fg['Date'], utc = True, dayfirst = True)
    df_fg = df_fg.set_index("Date").sort_index()

    #Removes blank data
    df_fg = df_fg.fillna(method='ffill')
    
    #Makes fear index between 0-1
    df_fg["fg"] = df_fg["fg"]/100

    #Creates a moving averae of F&G for cleaning extremes
    fg_roll = 90
    df_fg["fg_MA"] = df_fg["fg"].rolling(fg_roll).mean()

    #Gets the results
    days_prev = 90
    
    if filename_metric == "Fear and Greed":
        val = df_fg.fg.iloc[-1]
        prev_val = df_fg.fg.iloc[-days_prev]
        min_val = df_fg.fg.min()
        max_val =df_fg.fg.max()

    else:
        val = df_fg.fg_MA.iloc[-1]
        prev_val = df_fg.fg_MA.iloc[-days_prev]
        min_val = df_fg.fg.min()
        max_val =df_fg.fg.max()

    return val, prev_val, min_val, max_val
    
    
@strl.cache_data   
def api_tech_bullet_data (metric, api_ID):
    
    filename_metric = metric
    url = api_ID #source of info for price

    #Parameters required for metric
    api_key = strl.secrets["API_TOKEN"]
    a = "BTC"    #token
    s = '2020-01-01' #start date - not mandatory
    u = '2021-01-01' #until date - not mandatory
    i = '24h'         #time step
    f = "CSV"        #output format 
    timestamp_format = "humanized" #time stamp format

    #Compiles parameters
    params = (("a", a),("i", i),("f", f),("timestamp_format",timestamp_format ),("api_key", api_key))

    #Generates data requests and extracts the content
    r = requests.get(url, params)
    r_content = r.content

    #Writes the CSV temporary file
    csv_file = open(filename_metric+'.csv', 'wb')
    csv_file.write(r_content)
    csv_file.close()

    #Reads dataframe from temp file
    dfp = pd.read_csv(filename_metric+'.csv', parse_dates = [0], dayfirst = True)
    os.remove(filename_metric+'.csv')

    #Renames colums
    dfp = dfp.rename(columns={"timestamp": "Date", "c": "close", "h":"high", "l":"low", "o":"open" })

    #Removes blank data
    dfp = dfp.fillna(method='ffill')

    #Estimates number of days since inception "X"
    df = dfp
    df["DSI"] = df.index + 1
    df['Date']= pd.to_datetime(df['Date'], utc = True)
    df = df.set_index("Date")

    # 4.Fitting Polynomial Regression to the price
    X = np.log(df["DSI"].values).reshape(-1,1)
    Y = np.log(df["close"].values).reshape(-1,1)
    poly_reg = PolynomialFeatures(degree=3) #Defines the polinomial degree
    X_poly = poly_reg.fit_transform(X)
    pol_reg = LinearRegression()
    pol_reg.fit(X_poly, Y)

    #Estimates the regressed price
    df["price_reg"] = np.exp(pol_reg.predict(poly_reg.fit_transform(np.log(df["DSI"].values.reshape(-1,1)))))

    #Summary statistics
    SE_reg = np.sqrt(metrics.mean_squared_error(np.log(df.close), np.log(df.price_reg)))
    R2_reg = metrics.r2_score(np.log(df.close), np.log(df.price_reg))

    #5. Creates a normalization variable
    df["norm_dist"] = df.apply(lambda x: norm.cdf(np.log(x['close']), np.log(x['price_reg']), SE_reg),axis = 1)

    #6. Defines time (day) parameters for risk. Roll_long cannot be more than 326 as it will exclude the peak
    roll_short = 7
    roll_long = 350 #interesting 140

    #Moving average and risk index generated
    df["MA_short"] = df["close"].rolling(roll_short).mean()
    df["MA_long"] = df["close"].rolling(roll_long).mean()

    #Risk according to moving averages
    df["risk_MA"] = np.log(df["MA_short"]/df["MA_long"])

    SE_risk_MA = df["risk_MA"].std()
    mean_risk_MA = df["risk_MA"].mean()

    #Creates a normalization variable
    df["risk_MA_norm"] = df.apply(lambda x: norm.cdf(x['risk_MA'], mean_risk_MA, SE_risk_MA),axis = 1)

    #Gets the results
    days_prev = 90

    if metric == "MA log rat":
        var_select = "risk_MA_norm"
        val = df[var_select].iloc[-1]
        prev_val = df[var_select].iloc[-days_prev]
        min_val = df[var_select].min()
        max_val = df[var_select].max()

    else:
        var_select = "norm_dist"
        val = df[var_select].iloc[-1]
        prev_val = df[var_select].iloc[-days_prev]
        min_val = df[var_select].min()
        max_val =df[var_select].max()

    return val, prev_val, min_val, max_val


def market_data():
    
    base_url = "https://api.coingecko.com/api/v3"

    #Market percentages
    url = base_url + f"/global"
    r = requests.get(url)
    response = r.json()

    btc_per = response["data"]["market_cap_percentage"]["btc"]
    eth_per = response["data"]["market_cap_percentage"]["eth"]

    #Market prices
        #Bitcoin
    url = base_url + f"/simple/price?ids=bitcoin&vs_currencies=usd"
    r = requests.get(url)
    response = r.json()
    btc_price = response['bitcoin']['usd']

        #Ethereum
    url = base_url + f"/simple/price?ids=ethereum&vs_currencies=usd"
    r = requests.get(url)
    response = r.json()
    eth_price = response['ethereum']['usd']

    #Circulating supply
        #BTC
    url = base_url + "/coins/bitcoin?tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false"
    r = requests.get(url)
    response = r.json()
    btc_mcap = response["market_data"]["circulating_supply"]*btc_price

        #ETH
    url = base_url + "/coins/ethereum?tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false"
    r = requests.get(url)
    response = r.json()
    eth_mcap = response["market_data"]["circulating_supply"]*eth_price

    #Total market cap
    crypto_mcap = btc_mcap/(btc_per/100)

    return round(btc_price,1), round(eth_price, 1), round(btc_per,1), round(eth_per, 1), round(btc_mcap,1), round(eth_mcap,1), round(crypto_mcap,1)

@strl.cache_data
def api_btc_hist_price():
    # price --------------------------------------------------------
    api_ID = "https://api.glassnode.com/v1/metrics/market/price_usd_ohlc"
    filename_metric = "price"
    url = api_ID #source of info for price

    #Parameters required for metric
    api_key = "d27e087b-a489-4905-9ce9-2283bbc06f91"
    a = "BTC"    #token
    s = '2020-01-01' #start date - not mandatory
    u = '2021-01-01' #until date - not mandatory
    i = '24h'         #time step
    f = "CSV"        #output format 
    timestamp_format = "humanized" #time stamp format

    #Compiles parameters
    params = (("a", a),("i", i),("f", f),("timestamp_format",timestamp_format ),("api_key", api_key))

    #Generates data requests and extracts the content
    r = requests.get(url, params)
    r_content = r.content

    #Writes the CSV temporary file
    csv_file = open(filename_metric+'.csv', 'wb')
    csv_file.write(r_content)
    csv_file.close()

    #Reads dataframe from temp file
    dfp = pd.read_csv(filename_metric+'.csv', parse_dates = [0], dayfirst = True)
    os.remove(filename_metric+'.csv')

    #Renames colums
    dfp = dfp.rename(columns={"timestamp": "Date", "c": "close", "h":"high", "l":"low", "o":"open" })

    #Removes blank data
    dfp = dfp.fillna(method='ffill')

    #Estimates number of days since inception "X"
    df = dfp[["Date", "open", "high", "low", "close"]]

    df = df.set_index("Date")
    
    return df

@strl.cache_data
def api_fg_hist_data(metric, api_ID):
    #URL required for metric
    filename_metric = metric
    url = api_ID #source of info for price

    #Generates data requests and extracts the content
    r = requests.get(url)
    r_content = r.content

    #Writes the CSV file
    csv_file = open(filename_metric+'.csv', 'wb')
    csv_file.write(r_content)
    csv_file.close()

    #Cleans an formats database
        #Slices correct data
    df_fg = pd.read_csv(filename_metric+'.csv', header = 3)
    os.remove(filename_metric+'.csv')
    df_fg = df_fg.iloc[:-5]

        #Renames data
    df_fg = df_fg.rename(columns={"fng_value": "Date", "fng_classification": "fg", "date":"fg_cat"})

        #Sets Date as index
    df_fg['Date']= pd.to_datetime(df_fg['Date'], utc = True, dayfirst = True)
    df_fg = df_fg.set_index("Date").sort_index()

    #Removes blank data
    df_fg = df_fg.ffill(axis=0)

    #Makes fear index between 0-1
    df_fg["fg"] = df_fg["fg"]/100

    #Creates a moving averae of F&G for cleaning extremes
    fg_roll = 90
    df_fg["fg_MA"] = df_fg["fg"].rolling(fg_roll).mean()
    
    #Renames
    df_fg = df_fg.rename(columns={"fg": "Fear and Greed", "fg_MA": "Fear and Greed MA"})

    if metric == "Fear and Greed":
        df = df_fg[["Fear and Greed"]]

    else:
        df = df_fg[["Fear and Greed MA"]]
        
    return df

@strl.cache_data
def api_gn_hist_data(metric, api_ID):

    #URL required for metric
    filename_metric = metric
    url = api_ID #source of info for price

    #Parameters required for metric
    api_key = "d27e087b-a489-4905-9ce9-2283bbc06f91"
    a = "BTC"    #token
    s = '2020-01-01' #start date - not mandatory
    u = '2021-01-01' #until date - not mandatory
    i = '24h'         #time step
    f = "CSV"        #output format 
    timestamp_format = "humanized" #time stamp format

    #Compiles parameters
    params = (("a", a),("i", i),("f", f),("timestamp_format",timestamp_format ),("api_key", api_key))

    #Generates data requests and extracts the content
    r = requests.get(url, params)
    r_content = r.content

    #Writes the CSV temporary file
    csv_file = open(filename_metric+'.csv', 'wb')
    csv_file.write(r_content)
    csv_file.close()

    #Reads dataframe from temp file
    df = pd.read_csv(filename_metric+'.csv', parse_dates = [0], dayfirst = True)
    
    #Deletes file
    os.remove(filename_metric+'.csv')
    
    #Renames
    df = df.rename(columns={"timestamp": "Date", "value": metric})
    
    #Indexes
    df = df.set_index("Date")

    return df

@strl.cache_data
def api_tech_hist_data(metric, api_ID):

    filename_metric = metric
    url = api_ID #source of info for price

    #Parameters required for metric
    api_key = "d27e087b-a489-4905-9ce9-2283bbc06f91"
    a = "BTC"    #token
    s = '2020-01-01' #start date - not mandatory
    u = '2021-01-01' #until date - not mandatory
    i = '24h'         #time step
    f = "CSV"        #output format 
    timestamp_format = "humanized" #time stamp format

    #Compiles parameters
    params = (("a", a),("i", i),("f", f),("timestamp_format",timestamp_format ),("api_key", api_key))

    #Generates data requests and extracts the content
    r = requests.get(url, params)
    r_content = r.content

    #Writes the CSV temporary file
    csv_file = open(filename_metric+'.csv', 'wb')
    csv_file.write(r_content)
    csv_file.close()

    #Reads dataframe from temp file
    dfp = pd.read_csv(filename_metric+'.csv', parse_dates = [0], dayfirst = True)
    os.remove(filename_metric+'.csv')

    #Renames colums
    dfp = dfp.rename(columns={"timestamp": "Date", "c": "close", "h":"high", "l":"low", "o":"open" })

    #Removes blank data
    dfp = dfp.fillna(method='ffill')

    #Estimates number of days since inception "X"
    df = dfp
    df["DSI"] = df.index + 1
    df['Date']= pd.to_datetime(df['Date'], utc = True)
    df = df.set_index("Date")

    # 4.Fitting Polynomial Regression to the price
    X = np.log(df["DSI"].values).reshape(-1,1)
    Y = np.log(df["close"].values).reshape(-1,1)
    poly_reg = PolynomialFeatures(degree=3) #Defines the polinomial degree
    X_poly = poly_reg.fit_transform(X)
    pol_reg = LinearRegression()
    pol_reg.fit(X_poly, Y)

    #Estimates the regressed price
    df["price_reg"] = np.exp(pol_reg.predict(poly_reg.fit_transform(np.log(df["DSI"].values.reshape(-1,1)))))

    #Summary statistics
    SE_reg = np.sqrt(metrics.mean_squared_error(np.log(df.close), np.log(df.price_reg)))
    R2_reg = metrics.r2_score(np.log(df.close), np.log(df.price_reg))

    #5. Creates a normalization variable
    df["norm_dist"] = df.apply(lambda x: norm.cdf(np.log(x['close']), np.log(x['price_reg']), SE_reg),axis = 1)

    #6. Defines time (day) parameters for risk. Roll_long cannot be more than 326 as it will exclude the peak
    roll_short = 7
    roll_long = 350 #interesting 140

    #Moving average and risk index generated
    df["MA_short"] = df["close"].rolling(roll_short).mean()
    df["MA_long"] = df["close"].rolling(roll_long).mean()

    #Risk according to moving averages
    df["risk_MA"] = np.log(df["MA_short"]/df["MA_long"])

    SE_risk_MA = df["risk_MA"].std()
    mean_risk_MA = df["risk_MA"].mean()

    #Creates a normalization variable
    df["risk_MA_norm"] = df.apply(lambda x: norm.cdf(x['risk_MA'], mean_risk_MA, SE_risk_MA),axis = 1)

    if metric == "MA log rat":
        var_select = "risk_MA_norm"
        df = df[[var_select]]
        
        #Renames
        df = df.rename(columns={"timestamp": "Date", var_select: metric})

    else:
        var_select = "norm_dist"
        df = df[[var_select]]
        
        #Renames
        df = df.rename(columns={"timestamp": "Date", var_select: metric})
    
    return df


@strl.cache_data
def colored_metric(df, metric_name, metric_format):

    fig = go.Figure()

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["close"],
        mode = 'markers',
        name = 'Price',
        customdata = df[metric_name],
        hovertemplate='<br>'.join([
                '$%{y:'+'.1f'+'}',
                metric_name + ': %{customdata:' + metric_format + '}',
            ]),
        marker=dict(size=3,color = df[metric_name],showscale=True, colorscale= "jet") #[[0, 'rgb(0,0,255)'], [1, 'rgb(255,0,0)']]) #colorscale='Jet'
        ),secondary_y=False)

    #Defines figure properties
    fig.update_layout(
        title = metric_name,
        xaxis_title= "Date",
        yaxis_title= "USD/BTC",
        yaxis_type="log",
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
    )
    
    return fig

@strl.cache_data
def bounded_metric(df, metric_name, range_vals, metric_format = ".1f", log_scale = False):

    min_lim = range_vals[0]
    low_lim = range_vals[1]
    high_lim = range_vals[2]
    max_lim = range_vals[3]
    
    #Preprocessing inputs
    mid_lim = (low_lim + high_lim)/2

    if log_scale == True:
        log_scale_val = "log"

    else:
        log_scale_val = "linear"

    #Plotting
    fig = go.Figure()

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name = "BTC price"
            ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df[metric_name],
        mode = 'lines',
        name = metric_name,
        customdata = df[metric_name],
        hovertemplate='<br>'.join([
                '%{customdata:' + metric_format + '}',
            ]),
        marker=dict(size=3,color = "mediumblue")
        ),secondary_y=True)

    #Colors areas
    fig.add_hrect(y0=high_lim, y1=df[metric_name].max(), line_width=1, fillcolor="lightcoral", opacity=0.2, secondary_y = True)
    fig.add_hrect(y0=mid_lim, y1=high_lim, line_width=1, fillcolor="sandybrown", opacity=0.2, secondary_y = True)
    fig.add_hrect(y0=low_lim, y1=mid_lim, line_width=1, fillcolor="lemonchiffon", opacity=0.3, secondary_y = True)
    fig.add_hrect(y0=df[metric_name].min(), y1=low_lim, line_width=1, fillcolor="greenyellow", opacity=0.2, secondary_y = True)

    #Defines figure properties
    fig.update_layout(
        title = metric_name,
        xaxis_title= "Date",
        yaxis_title= "USD/BTC",
        yaxis_type="log",
        yaxis2_type=log_scale_val,
        xaxis_rangeslider_visible=False,
        hovermode="x unified", 
    )

    return fig

def plot_graphs(df_meta, colored = False):

    #Historic price
    df_price = api_btc_hist_price()

    # Runs functions in loops
    for i, metric in enumerate(df_meta["metric_name"]):

        # Defines the source of data to be used
        if df_meta.iloc[i]["type"] == "Onchain":
            df_metric = api_gn_hist_data(metric, df_meta.iloc[i]["api_id"])
        elif df_meta.iloc[i]["type"] == "Technical":
            df_metric = api_tech_hist_data(metric, df_meta.iloc[i]["api_id"])
        else:
            df_metric = api_fg_hist_data(metric, df_meta.iloc[i]["api_id"])

        # Defines ranges to be used
        if df_meta.iloc[i]["custom_limit"] == True:
            range_vals = [df_meta.iloc[i]["min"], df_meta.iloc[i]["low"], df_meta.iloc[i]["high"], df_meta.iloc[i]["max"]]

        else:
            range_vals = [df_metric[metric].min(), df_meta.iloc[i]["low"], df_meta.iloc[i]["high"], df_metric[metric].max()]

        #merges data
        df = df_price.merge(df_metric, how = "outer", left_index=True, right_index=True)
        df = df.reset_index()

        if colored == True:
            strl.plotly_chart(colored_metric(df, metric, df_meta.iloc[i]["format"]))

        else:
            strl.plotly_chart(bounded_metric(df, metric, range_vals, df_meta.iloc[i]["format"], log_scale = df_meta.iloc[i]["log_scale"] ))


@strl.cache_data
def unified_df(df_meta):

    #Historic price
    df_price = api_btc_hist_price()

    # Runs functions in loops
    for i, metric in enumerate(df_meta["metric_name"]):

        # Defines the source of data to be used
        if df_meta.iloc[i]["type"] == "Onchain":
            df_metric = api_gn_hist_data(metric, df_meta.iloc[i]["api_id"])
        elif df_meta.iloc[i]["type"] == "Technical":
            df_metric = api_tech_hist_data(metric, df_meta.iloc[i]["api_id"])
        else:
            df_metric = api_fg_hist_data(metric, df_meta.iloc[i]["api_id"])

        # Defines ranges to be used
        min_val = df_metric[metric].min()
        max_val = df_metric[metric].max()
        range_vals = [min_val, df_meta.iloc[i]["low"], df_meta.iloc[i]["high"], max_val ]
        
        #Log normalization
        log_scale = df_meta.iloc[i]["log_scale"]
        if log_scale == True:
            df_metric[metric] = np.log(df_metric[metric])
            min_val = np.log(min_val)
            max_val = np.log(max_val)
        
        #Normalizes
        df_metric[metric] = (df_metric[metric] - min_val)/(max_val-min_val)

        #merges data
        df_price = df_price.merge(df_metric, how = "outer", left_index=True, right_index=True)
        df = df_price.reset_index()
        
        print(metric + " added to database")
    
    #Sets dataframe
    df = df.set_index("Date")
    df = df.ffill(axis=0)
    
    return df


@strl.cache_data
def bull_bear_classifier(df,bull_bear_map):
    
    #Initial conditions
    prev_date = df["close"].first_valid_index().strftime('%Y-%m-%d')
    prev_bull_bear = "bull"
    df["bull_bear"] = "Unclassificed"
    
    #Makes classification
    for i, item in enumerate(bull_bear_map):
        day, month, year, val, bull_bear = item.split(" ")
        date_peak_bot = str(year) + "-" + str(month) + "-" + str(day)

        if  i != 0:
            df.loc[prev_date:date_peak_bot, "bull_bear"]= prev_bull_bear

            prev_date = date_peak_bot
            prev_bull_bear = bull_bear
            
    return df

@strl.cache_data
def ML_date_finder(df, selected_Xvariables):
    #Finds initial possible date with current variable selection
    start_date = df.index[0]
    for col in selected_Xvariables:
        if df[col].first_valid_index() > start_date:
            start_date = df[col].first_valid_index()

    start_date = start_date.strftime('%Y-%m-%d')

    return start_date

@strl.cache_data
def ML_XY_dataselector(df, selected_Xvariables, Yvariable, start_date, mid_date, end_date):

    #Defines dates to slice data
    X_train = df.loc[start_date:mid_date][selected_Xvariables].values
    y_train = df.loc[start_date:mid_date][[Yvariable]].values

    X_test = df.loc[mid_date:end_date][selected_Xvariables].values
    y_test = df.loc[mid_date:end_date][[Yvariable]].values
    
    return X_train, y_train, X_test, y_test, [start_date, mid_date, end_date]

@strl.cache_resource
def ML_model_traintest(X_train, y_train, X_test, y_test, mod_type = "rfc"):

    if mod_type == 'Random Forest':

        # Import the model we are using and instantiate model with 1000 decision trees
        model = RandomForestClassifier() #n_estimators = 1000, random_state = 42)# Train the model on training data

    elif mod_type == "Support Vector Machine":
        #Create a svm Classifier
        model = svm.SVC(kernel='linear') # Linear Kernel

    elif mod_type == "K-NN":
        #Creates knn classfifier
        model = KNeighborsClassifier() #n_neighbors=3)

    elif mod_type == "Naive Bayes":
        #Naive Bayes
        model = GaussianNB()

    elif mod_type == "Logistic regression":
        #Logistic regression
        model = LogisticRegression()

    else:
        #Decision tree
        model = DecisionTreeClassifier()


    # Fits data
    model.fit(X_train, y_train.ravel())

    # Use the forest's predict method on the test data
    y_pred = model.predict(X_test)# Calculate the absolute errors
    
    # Model Accuracy, how often is the classifier correct?
    accuracy = metrics.accuracy_score(y_test, y_pred)
    
    return model, accuracy

def ML_model_predict(model, df, selected_variables, start_date):
    
    #Finds today date to define the las available data on time series data frame
    # last_val_date = (date.today() -  timedelta(days=1)).strftime('%Y-%m-%d') #Debugged code

    #Slices dataframe
    X_new  = df.loc[start_date:][selected_variables].iloc[:-1].values
    df_new = df.loc[start_date:].iloc[:-1]
    df_new["bull_bear_pred"] = model.predict(X_new)
    
    return df_new

def ML_bull_bear_plot(df_in, start_date, mid_date, end_date, mod_type):
    
    #Encodes bull bear
    cleanup_nums = {"bull_bear":     {"bull": 1, "bear": 0, 'Unclassificed':0.5 },
                    "bull_bear_pred": {"bull": 1, "bear": 0}
                   }

    df = df_in.replace(cleanup_nums)

    # Creates horizontal line y = 1 to define bulish and bearish zones
    df["hor"] = 1

    #Defines error
    df["error"] = df.apply(lambda x: 0.25 if x["bull_bear"] != x["bull_bear_pred"] else 0, axis = 1 )
    df["error"].loc[end_date:] = 0

    #Plotting
    fig = go.Figure()

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name = "BTC price"
            )) 

    # Adds bear bull prediction   
    fig.add_trace(go.Scatter(
                            x=df.index, y=df["bull_bear_pred"], 
                            mode = 'markers', 
                            name = "Bullish period", 
                            marker=dict(size=0.1,color = "green", opacity = 0.01),
                            fill='tozeroy',
                            fillcolor='rgba(60,179,113,0.2)',
                            opacity=0, 
                            ),secondary_y=True)
    
    # Adds horizontal line and fills in teh are with red
    fig.add_trace(go.Scatter(
                            x=df.index, y=df["hor"], 
                            mode = 'markers', 
                            name = "Bearish period", 
                            marker=dict(size=0.1,color = "red", opacity = 0.01),
                            fill='tonexty',
                            fillcolor='rgba(255,0,0,0.2)',
                            opacity=0,
                            ),secondary_y=True)

    # Adds bars for error
    fig.add_trace(go.Bar(
                            x=df.index, y=df["error"], 
                            # mode = 'lines', 
                            name = "Classification error",
                            marker_color= "orange" 
                            # marker=dict(size=1,color = "orange"),
                            # fill='tonexty',
                            # opacity=0
                            ),secondary_y=True)
    
    #Adds vertical line in the split data time
    fig.add_vline(x=start_date, line_width=2, line_dash="dash", line_color="grey")
    fig.add_annotation(x=start_date, xanchor = "left",
                       y = 1, yref = "paper", yanchor = "top", secondary_y=True,
                       showarrow=False, textangle = 0,  text="Training data")

    fig.add_vline(x=mid_date, line_width=2, line_dash="dash", line_color="grey")
    fig.add_annotation(x=mid_date, xanchor = "left",
                       y = 1, yref = "paper", yanchor = "top", secondary_y=True,
                       showarrow=False, textangle = 0,  text="Test data")

    fig.add_vline(x=end_date, line_width=2, line_dash="dash", line_color="grey")
    fig.add_annotation(x=end_date, xanchor = "left",
                       y = 1, yref = "paper", yanchor = "top", secondary_y=True,
                       showarrow=False, textangle = 0, text="Unclassified data")
    
    #Updates figure
    fig.update_layout(
        title = mod_type + " bull/bear classification",
        xaxis_title= "Date",
        yaxis_title= "USD/BTC",
        # yaxis2_title = "Bull-Bear",
        yaxis_type="log",
#         yaxis2_type=log_scale_val,
        xaxis_rangeslider_visible=False,
        hovermode="x unified", 
    )

    fig.update_yaxes(secondary_y=True, showgrid=False, visible = False)
    
    return fig

# ===========FUNCTIONS V2=========================
@strl.cache_data
def aws_crypto_api(url, metric, price_bool, normalize_bool, api_key):
    
    params = (("metric",metric),
          ("price_bool", price_bool),
          ("normalize_bool",normalize_bool),
          ("api_key", api_key))

    #Generates data requests and extracts the content
    r = requests.get(url, params)
    r_content = r.json()

    return pd.read_json(r_content[metric], orient ='index')

@strl.cache_data
def plot_graphsV2(df_data, df_meta, colored = False):

     # Runs functions in loops
    for i, metric in enumerate(df_meta["metric_name"]):

        df_plot = df_data[["open","high","low","close", metric]]

        # Defines ranges to be used
        if df_meta.iloc[i]["custom_limit"] == True:
            range_vals = [df_meta.iloc[i]["min"], df_meta.iloc[i]["low"], df_meta.iloc[i]["high"], df_meta.iloc[i]["max"]]

        else:
            range_vals = [df_plot[metric].min(), df_meta.iloc[i]["low"], df_meta.iloc[i]["high"], df_plot[metric].max()]

        if colored == True:
            strl.plotly_chart(colored_metric(df_plot, metric, df_meta.iloc[i]["format"]))

        else:
            strl.plotly_chart(bounded_metric(df_plot, metric, range_vals, df_meta.iloc[i]["format"], log_scale = df_meta.iloc[i]["log_scale"] ))