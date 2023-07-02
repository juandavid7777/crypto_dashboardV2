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
from sklearn.neural_network import MLPClassifier
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
def market_data(date_today):
    
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
def colored_metric(df, metric_name, metric_format, color_map = [[0,"lawngreen"],[0.2,"greenyellow"], [0.4,"lemonchiffon"], [0.6,"sandybrown"], [0.8,"lightcoral"], [1,"crimson"]], interactive = True):

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
        marker=dict(size=3,color = df[metric_name],showscale=True, colorbar=dict(title = metric_name), colorscale= color_map), #[[0, 'rgb(0,0,255)'], [1, 'rgb(255,0,0)']]) #colorscale='Jet'
        # color_continuous_scale=["red", "green", "blue"]
        ),secondary_y=False)
    
    if interactive != True:

        dark_theme = "#262730" #"#0E1117" #"rgba(0, 0, 0, 0.95)"
        fig.update_layout(shapes=[dict(
            type="rect",
            xref="paper",
            yref="paper",
            x0 = 0,
            y0= 0,
            x1= 1,
            y1= 1,
            fillcolor=dark_theme,
            opacity = 0.98,
            layer="above",
            line_width=0,
                        )
                        ]   
                        )

    #Defines figure properties
    fig.update_layout(
        title = metric_name,
        xaxis_title= "Date",
        yaxis_title= "USD/BTC",
        yaxis_type="log",
        coloraxis_colorbar=dict(title="Your Title"),
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        autosize=True,
    )

    return fig

@strl.cache_data
def bounded_metric(df, metric_name, range_vals, metric_format = ".1f", log_scale = False, interactive = True):

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
        marker=dict(size=3,color = "orange")
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
        autosize=True, 
    )

    #Adds secodnary title
    fig.update_yaxes(title_text=metric_name, secondary_y=True)

    if interactive != True:

        dark_theme = "#262730" #"#0E1117" #"rgba(0, 0, 0, 0.95)"
        fig.add_hrect(y0=df[metric_name].min(), y1=df[metric_name].max(), line_width=0, fillcolor=dark_theme, opacity=0.98, secondary_y = True)

    return fig


# ===========MACHINE LEARNING FUNCTIONS=========================

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

def ML_date_finder(df, selected_Xvariables):
    #Finds initial possible date with current variable selection
    start_date = df.index[0]
    for col in selected_Xvariables:
        if df[col].first_valid_index() > start_date:
            start_date = df[col].first_valid_index()

    start_date = start_date.strftime('%Y-%m-%d')

    return start_date

def ML_XY_dataselector(df, selected_Xvariables, Yvariable, start_date, mid_date, end_date):

    #Defines dates to slice data
    X_train = df.loc[start_date:mid_date][selected_Xvariables].values
    y_train = df.loc[start_date:mid_date][[Yvariable]].values

    X_test = df.loc[mid_date:end_date][selected_Xvariables].values
    y_test = df.loc[mid_date:end_date][[Yvariable]].values
    
    return X_train, y_train, X_test, y_test, [start_date, mid_date, end_date]

@strl.cache_resource
def ML_model_traintest(X_train, y_train, X_test, y_test, mod_type = "Random Forest"):

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

    elif mod_type == "Logistic Regression":
        #Logistic regression
        model = LogisticRegression()

    elif mod_type == "Decision Tree":
        #Decision tree
        model = DecisionTreeClassifier()

    else:
        #Neural Network
        model = MLPClassifier()


    # Fits data
    model.fit(X_train, y_train.ravel())

    # Use the forest's predict method on the test data
    y_pred = model.predict(X_test)# Calculate the absolute errors

    #Uses model to predict in all data
    X_all = np.append(X_train,X_test, axis=0)    
    y_pred_all = model.predict(X_all)
    
    # Model Accuracy, how often is the classifier correct?
    accuracy = metrics.accuracy_score(y_test, y_pred)
    accuracy_all = metrics.accuracy_score(np.append(y_train,y_test), y_pred_all)
    
    return model, accuracy, accuracy_all

def ML_model_predict(model, df, selected_variables, start_date, model_name = "bull_bear_pred"):
    
    #Finds today date to define the las available data on time series data frame
    # last_val_date = (date.today() -  timedelta(days=1)).strftime('%Y-%m-%d') #Debugged code

    #Slices dataframe
    X_new  = df.loc[start_date:][selected_variables].iloc[:-1].values
    df_new = df.loc[start_date:].iloc[:-1]
    df_new[model_name] = model.predict(X_new)
    
    return df_new

@strl.cache_data
def ML_bull_bear_plot(df_in, start_date, mid_date, end_date, title = "Title", interactive = True):

    if interactive != True:
        interactive = False

    df_in["bull_bear_cat"] = df_in["bull_bear_pred"]
    
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

    
    fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name = "BTC price"
            )) 
    
    #Adds vertical line in the split data time
    fig.add_vline(x=start_date, line_width=2, line_dash="dash", line_color="grey")
    fig.add_annotation(x=start_date, xanchor = "left",
                       y = 1, yref = "paper", yanchor = "top", secondary_y=True,
                       showarrow=False, textangle = 90,  text="Training data", visible = interactive)

    fig.add_vline(x=mid_date, line_width=2, line_dash="dash", line_color="grey")
    fig.add_annotation(x=mid_date, xanchor = "left",
                       y = 1, yref = "paper", yanchor = "top", secondary_y=True,
                       showarrow=False, textangle = 90,  text="Test data", visible = interactive)

    fig.add_vline(x=end_date, line_width=2, line_dash="dash", line_color="grey")
    fig.add_annotation(x=end_date, xanchor = "left",
                       y = 1, yref = "paper", yanchor = "top", secondary_y=True,
                       showarrow=False, textangle = 90, text="Unclassified data", visible = interactive)
    
    if interactive != True:

        dark_theme = "#262730" #"#0E1117" #"rgba(0, 0, 0, 0.95)"
        fig.update_layout(shapes=[dict(
            type="rect",
            xref="paper",
            yref="paper",
            x0 = 0,
            y0= 0,
            x1= 1,
            y1= 1,
            fillcolor=dark_theme,
            opacity = 0.70,
            layer="above",
            line_width=0,
                        )
                        ]   
                        )

    #Updates figure
    fig.update_layout(
        title = title + " - " + df_in["bull_bear_cat"].iloc[-1] + " trend",
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
def aws_crypto_api(url, metric, price_bool, normalize_bool, api_key, today_date):
    
    params = (("metric",metric),
          ("price_bool", price_bool),
          ("normalize_bool",normalize_bool),
          ("api_key", api_key))

    #Generates data requests and extracts the content
    r = requests.get(url, params)
    r_content = r.json()

    df = pd.read_json(r_content[metric], orient ='index')
    df.index = pd.to_datetime(df.index)

    return df

@strl.cache_data
def plot_graphsV2(df_data, df_meta, render, render_config, colored = False, ):

     # Runs functions in loops
    for i, metric in enumerate(df_meta["metric_name"]):

        df_plot = df_data[["open","high","low","close", metric]]

        # Defines ranges to be used
        if df_meta.iloc[i]["custom_limit"] == True:
            range_vals = [df_meta.iloc[i]["min"], df_meta.iloc[i]["low"], df_meta.iloc[i]["high"], df_meta.iloc[i]["max"]]

        else:
            range_vals = [df_plot[metric].min(), df_meta.iloc[i]["low"], df_meta.iloc[i]["high"], df_plot[metric].max()]

        if colored == True:
            strl.plotly_chart(colored_metric(df_plot, metric, df_meta.iloc[i]["format"], interactive = render), use_container_width=True, config = render_config)

        else:
            strl.plotly_chart(bounded_metric(df_plot, metric, range_vals, df_meta.iloc[i]["format"], log_scale = df_meta.iloc[i]["log_scale"], interactive = render), use_container_width=True, config = render_config)


#Function for soft voting ML
@strl.cache_data
def soft_vote_ML(df_classified, selected_variables, model_type_list, start_date, mid_date, end_date, rolling_vote_window = 7):

    #Intiate dataframe accuracies
    df_accuracy = pd.DataFrame()
    cleanup_nums = {}

    for i, model_type in enumerate(model_type_list):

        #Splits the data
        X_train, y_train, X_test, y_test, split_dates_list = ML_XY_dataselector(df_classified, selected_variables, "bull_bear", start_date, mid_date, end_date)

        start_date = split_dates_list[0]
        mid_date = split_dates_list[1]
        end_date = split_dates_list[2]

        #Trains the model
        model, accuracy_test, accuracy_all = ML_model_traintest(X_train, y_train, X_test, y_test, mod_type = model_type)


        # Uses the model with new data to predict 
        df_classified = ML_model_predict(model,
                                        df_classified,
                                        selected_variables,
                                        start_date,
                                        model_type
                                        )
        
        df_temp = pd.DataFrame({"Model":[model_type],
                                "Test acc.": [accuracy_test],
                                "Total acc.": [accuracy_all],                            
                              })
        
        # cleanup_nums[model_type] = {'bull': accuracy_test, 'bear': -accuracy_test}
        cleanup_nums[model_type] = {'bull': 1, 'bear': -1}
        df_accuracy = pd.concat([df_accuracy,df_temp], ignore_index=True)
        
    # Numeric classification    
    df_allclassified = df_classified.replace(cleanup_nums)
    df_allclassified['soft_vote'] = df_allclassified[model_type_list].mean(axis=1)

    # Define entry points
    df_allclassified["rolling_vote"] = df_allclassified['soft_vote'].rolling(rolling_vote_window).mean()
    df_allclassified["bull_bear_pred"] = df_allclassified.apply(lambda x: "bull" if x["rolling_vote"]>0 else "bear", axis = 1)

    #Defines bar graphs and bull bear trend
    df_allclassified["bar_vote"] = (abs(df_allclassified["rolling_vote"])/2)+0.5

    return df_allclassified, df_accuracy

@strl.cache_data
def soft_vote_plot(df_in, start_date, mid_date, end_date, conf_threshold = 0.8, interactive = True):

    if interactive != True:
        interactive = False

    #Creates copy of trend  
    df_in["bull_bear_cat"] = df_in["bull_bear"]
    df_in["bull_bear_pred_cat"] = df_in["bull_bear_pred"]

    #Finds accuracy
    y_test = df_in.loc[start_date:end_date][["bull_bear"]].values
    y_pred = df_in.loc[start_date:end_date][["bull_bear_pred"]].values

    soft_vote_accuracy = metrics.accuracy_score(y_test, y_pred)

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

    #Scale for defining max of the bull ebar areas
    scaling =  df['high'].max()

    # Adds bear bull prediction
    fig.add_trace(go.Scatter(
                            x=df.index, y=df["bull_bear_pred"]*scaling, 
                            mode = 'markers', 
                            name = "Bullish period", 
                            marker=dict(size=0.1,color = "green", opacity = 0.01),
                            fill='tozeroy',
                            fillcolor='rgba(60,179,113,0.2)',
                            opacity=0,
                            hoverinfo='skip' 
                            ),secondary_y=False)
    
    
    
    # Adds horizontal line and fills in teh are with red
    fig.add_trace(go.Scatter(
                            x=df.index, y=df["hor"]*scaling, 
                            mode = 'markers', 
                            name = "Bearish period", 
                            marker=dict(size=0.1,color = "red", opacity = 0.01),
                            fill='tonexty',
                            fillcolor='rgba(255,0,0,0.2)',
                            opacity=0,
                            hoverinfo='skip'
                            ),secondary_y=False)

       
    #Soft vote line mapping
    df["bull_conf"] = df.apply(lambda x: x["bar_vote"] if ((x["bull_bear_pred"] == 1) & (x["bar_vote"] > conf_threshold)) else 0, axis = 1)
    df["bear_conf"] = df.apply(lambda x: x["bar_vote"] if ((x["bull_bear_pred"] == 0) & (x["bar_vote"] > conf_threshold)) else 0, axis = 1)
    df["uncertain"] = df.apply(lambda x: x["bar_vote"] if (x["bar_vote"] <= conf_threshold) else 0, axis = 1)

    fig.add_trace(go.Scatter(
            x=df.index,
            y=df["uncertain"]*100,
            mode='lines',
            line=dict(width=0.01, color='orange'),
            stackgroup='one',
            opacity=0,
            name='Mid uncertainity',
            hovertemplate='Uncertain area confidence: %{y:.1f}%<extra></extra>'
        ),secondary_y=True)

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["bear_conf"]*100,
        mode='lines',
        line=dict(width=0.01, color='red'),
        stackgroup='one',
        opacity=0,
        name='Bearish confidence',
        hovertemplate='Bear Confidence: %{y:.1f}%<extra></extra>'
    ),secondary_y=True)

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["bull_conf"]*100,
        mode='lines',
        line=dict(width=0.01, color='green'),
        stackgroup='one',
        opacity=0,
        name="Bullish confidence",
        hovertemplate='Bull Confidence: %{y:.1f}%<extra></extra>'
    ),secondary_y=True)

    # Adds lines for confidence
    fig.add_trace(go.Scatter(
                            x=df.index, y=df["bar_vote"]*100, 
                            mode = 'lines', 
                            name = "Confidence vote",
                            marker=dict(size=0.011,color = "#202020"),
                            opacity=0.5,
                            customdata=df["bull_bear_pred_cat"],
                            hovertemplate='Trend assessment: %{customdata}<extra></extra>'
                            ),secondary_y=True)
    
    #Adds prices
    fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name = "BTC price"
            ))

   
    #Adds vertical line in the split data time
    fig.add_vline(x=start_date, line_width=2, line_dash="dashdot", line_color="grey")
    fig.add_annotation(x=start_date, xanchor = "left",
                       y = 1, yref = "paper", yanchor = "top", secondary_y=True,
                       showarrow=False, textangle = 90,  text="Training data", visible = interactive)

    fig.add_vline(x=mid_date, line_width=2, line_dash="dashdot", line_color="grey")
    fig.add_annotation(x=mid_date, xanchor = "left",
                       y = 1, yref = "paper", yanchor = "top", secondary_y=True,
                       showarrow=False, textangle = 90,  text="Test data", visible = interactive)

    fig.add_vline(x=end_date, line_width=2, line_dash="dashdot", line_color="grey")
    fig.add_annotation(x=end_date, xanchor = "left",
                       y = 1, yref = "paper", yanchor = "top", secondary_y=True,
                       showarrow=False, textangle = 90, text="Unclassified data", visible = interactive)
    
    fig.add_hline(y=conf_threshold*100, line_width=1.5, line_dash="dot", line_color="orange", secondary_y=True)
    fig.add_annotation(y=conf_threshold*0.87,
                       x=0.05,
                       xref='paper',
                       yref='y',
                       showarrow=False,
                       textangle = 0,
                       text="Conf. Threshold: " + str(conf_threshold*100) + "%",
                       font=dict(color='#ffaf1a'),  # Set the color of the text to orange
                       secondary_y=True,
                       visible = interactive
                       )
    
    if interactive != True:

        dark_theme = "#262730" #"#0E1117" #"rgba(0, 0, 0, 0.95)"
        fig.update_layout(shapes=[dict(
            type="rect",
            xref="paper",
            yref="paper",
            x0 = 0,
            y0= 0,
            x1= 1,
            y1= 1,
            fillcolor=dark_theme,
            opacity = 0.65,
            layer="above",
            line_width=0,
                        )
                        ]   
                        )

    #Updates figure
    fig.update_layout(
        title = "Multi-vote confidence: " + str(round((soft_vote_accuracy*100), 2)) + " % - " + df["bull_bear_pred_cat"].iloc[-1] + " trend",
        xaxis_title= "Date",
        yaxis_title= "USD/BTC",
        yaxis_type="log",
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
    )

    fig.update_yaxes(secondary_y=True, 
                     title_text= "Trend confidence (%)", 
                     showgrid=True, 
                     visible = True, 
                     range = [50,250], 
                     tickvals=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90,100], 
                     gridcolor = '#bdbdbd')

    return fig

@strl.cache_data
def convert_df_tocsv(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')