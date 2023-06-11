import pandas as pd
import numpy as np
import streamlit as strl
import streamlit_authenticator as stauth

from streamlit_extras.buy_me_a_coffee import button
from streamlit_extras.badges import badge
from streamlit_extras.colored_header import colored_header 

import yaml

from datetime import date, timedelta
import datetime

from functions import bullet_fig_metric, market_data, aws_crypto_api, colored_metric, bounded_metric
from functions_auth import credentials_email, load_config, save_config, auth_connected, auth_disconnected, sidebar_auth, access_warning


# Initialize a session state variable that tracks the sidebar state (either 'expanded' or 'collapsed').
if 'sidebar_state' not in strl.session_state:
    strl.session_state.sidebar_state = 'expanded'

# Sets page configuration
strl.set_page_config(initial_sidebar_state=strl.session_state.sidebar_state, layout="wide", page_title="₿itcointrends", page_icon = "🚀")

#Gets latest price data
date_today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
btc_price, eth_price, btc_per, eth_per, btc_mcap, eth_mcap, crypto_mcap = market_data(date_today = date_today)

# Title
strl.image("bitcoin_strip.png", use_column_width = True)

# Donations
strl.subheader("Unlock the potential of data science and Bitcoin analysis to create a brighter financial future for all. Stay tunned, and keep accumulating!")
col1, col2, col3, col4 = strl.columns([1.5, 1.5, 5, 4])

with col1:
    badge(type="twitter", name="barbosa83")
with col2:
    badge(type="buymeacoffee", name="juandavid7E")
with col3:
    strl.caption("₿: 3EbH7JPSTGqSzyKKAijgva1ffXaY6JWk34")

strl.write("Bitcoin, the pioneering cryptocurrency, has experienced notable price cycles since its inception. These cycles often exhibit patterns influenced by various factors. One approach to understand and predict these cycles is by utilizing the concept of Bitcoin halving which defines a repetitive fundamental change which results in a reiteration of certain market dynamics. Building on this idea, a comprehensive analysis of nine metrics has been conducted, encompassing technical, on-chain, and sentiment indicators. By incorporating information from multiple sources, we implement a data-driven Machine Learning methodology to identify repeating patterns and map the market’s trend within the current cycle.")

# Summary market
colored_header(label = "", description = "", color_name="yellow-80")
strl.header("Market summary")
strl.caption("Powered by CoinGecko and Python Analytics")

col_mcap, col_per, col_price = strl.columns(3)

with col_mcap:
    strl.subheader("Market cap")
    strl.write("Crypto ", round(crypto_mcap/1000000000,1),"B")
    strl.write("BTC ", round(btc_mcap/1000000000,1),"B")
    strl.write("ETH ", round(eth_mcap/1000000000,1),"B")

with col_per:
    strl.subheader("Dominance")
    strl.write("BTC ", btc_per, "%")
    strl.write("ETH ", eth_per , "%")

with col_price:
    strl.subheader("Price")
    strl.write("BTC/USD ", btc_price)
    strl.write(" ETH/USD ", eth_price)

#Adds metrics in columns
strl.markdown("""---""")

#Adds side authenticator
sidebar_auth()

#Basic session rendering if connected
render_config = {'staticPlot': not(strl.session_state["authentication_status"]),
                 'displaylogo': False}
render = strl.session_state["authentication_status"]

#Sets API general parameters
aws_api_url = strl.secrets["aws_api_url"]
api_key = strl.secrets["aws_api_token"]
date_today = datetime.datetime.now().strftime("%Y-%m-%d")

#Calls metadata
metric = "Metadata"
price_bool = False
normalize_bool = False
df_metadata = aws_crypto_api(aws_api_url, metric, price_bool, normalize_bool, api_key, date_today)

#Calls all data
metric = "All"
price_bool = True
normalize_bool = False
df_data = aws_crypto_api(aws_api_url, metric, price_bool, normalize_bool, api_key,date_today)

#Plots bullet data metrics
strl.header("Metrics")

strl.write("The selected oscillating metrics consist of two technical indicators derived purely from price movements, five on-chain indicators based on wallet movements within the blockchain, and two sentiment indicators utilizing information extracted from social media platforms. Future work will add new metrics that follow an oscillating cyclic pattern that relates to the Bitcoin repeating dynamics. Common cyclic peaks (red), valleys (green) and mid-cycle (yellow & orange) areas can be identified in individual metrics, however, a confluence approach should be implemented to reduce the risk when classifying the market trend.")
strl.caption("Bullet figures below show the current value of the metric and the cycle area where has been mapped. For a historic visualization of each metric, check the Technical, On-chain and Sentiment sections. (Peak: red , Bottom: green, Mid-cycle: yellow & orange)")

col_tech, col_onchain, col_sent = strl.columns(3)

# Technical
with col_tech:
    strl.subheader("Technical")

    #Runs functions in loops
    df_meta = df_metadata[df_metadata["type"].isin(["Technical"])]

    for i, metric in enumerate(df_meta["metric_name"]):
        # Defines the source of data to be used

        time_shift = 90 #days

        val = df_data.iloc[-2][metric] 
        prev_val =  df_data.iloc[-time_shift][metric] 
        min_val = df_data[metric].min()
        max_val = df_data[metric].max()
    
        # Defines ranges to be used
        if df_meta.iloc[i]["custom_limit"] == True:
            range_vals = [df_meta.iloc[i]["min"], df_meta.iloc[i]["low"], df_meta.iloc[i]["high"], df_meta.iloc[i]["max"]]
            
        else:
            range_vals = [min_val, df_meta.iloc[i]["low"], df_meta.iloc[i]["high"], max_val]

        # Plots data
        fig = bullet_fig_metric(value_in = val,
                    previous_val = prev_val,
                    title_text = metric,
                    ranges = range_vals,
                    format_num = df_meta.iloc[i]["format"],
                    log_scale = df_meta.iloc[i]["log_scale"]
                    )
        
        strl.plotly_chart(fig, use_container_width=True)


# Onchain
with col_onchain:
    strl.subheader("Onchain")

    #Runs functions in loops
    df_meta = df_metadata[df_metadata["type"].isin(["Onchain"])]

    for i, metric in enumerate(df_meta["metric_name"]):
        # Defines the source of data to be used

        time_shift = 90 #days

        val = df_data.iloc[-2][metric] 
        prev_val =  df_data.iloc[-time_shift][metric] 
        min_val = df_data[metric].min()
        max_val = df_data[metric].max()
    
        # Defines ranges to be used
        if df_meta.iloc[i]["custom_limit"] == True:
            range_vals = [df_meta.iloc[i]["min"], df_meta.iloc[i]["low"], df_meta.iloc[i]["high"], df_meta.iloc[i]["max"]]
            
        else:
            range_vals = [min_val, df_meta.iloc[i]["low"], df_meta.iloc[i]["high"], max_val]

        # Plots data
        fig = bullet_fig_metric(value_in = val,
                    previous_val = prev_val,
                    title_text = metric,
                    ranges = range_vals,
                    format_num = df_meta.iloc[i]["format"],
                    log_scale = df_meta.iloc[i]["log_scale"]
                    )
        
        strl.plotly_chart(fig, use_container_width=True)

# Sentiment
with col_sent:
    strl.subheader("Sentiment")

    #Runs functions in loops
    df_meta = df_metadata[df_metadata["type"].isin(["Sentiment"])]

    for i, metric in enumerate(df_meta["metric_name"]):
        # Defines the source of data to be used

        time_shift = 90 #days

        val = df_data.iloc[-2][metric] 
        prev_val =  df_data.iloc[-time_shift][metric] 
        min_val = df_data[metric].min()
        max_val = df_data[metric].max()
    
        # Defines ranges to be used
        if df_meta.iloc[i]["custom_limit"] == True:
            range_vals = [df_meta.iloc[i]["min"], df_meta.iloc[i]["low"], df_meta.iloc[i]["high"], df_meta.iloc[i]["max"]]
            
        else:
            range_vals = [min_val, df_meta.iloc[i]["low"], df_meta.iloc[i]["high"], max_val]

        # Plots data
        fig = bullet_fig_metric(value_in = val,
                    previous_val = prev_val,
                    title_text = metric,
                    ranges = range_vals,
                    format_num = df_meta.iloc[i]["format"],
                    log_scale = df_meta.iloc[i]["log_scale"]
                    )
        
        strl.plotly_chart(fig, use_container_width=True)

strl.markdown("""----""")
   
#Calls all data
metric = "All"
price_bool = True
normalize_bool = True
df_data = aws_crypto_api(aws_api_url, metric, price_bool, normalize_bool, api_key,date_today)

#Confluence risk area
strl.header("Confluence risk")
strl.write("In order to prevent favoring any single metric and ensure a balanced approach, we have adopted a linear weight method. Each metric is first normalized on a scale of 0 to 1, allowing for fair comparison across different ranges. Subsequently, an average of all the normalized metrics is calculated to obtain a confluence risk value. This confluence metric serves as a powerful tool to filter out extraneous fluctuations and provide a comprehensive mapping of the generalized risk of Bitcoin within the market cycle.")

#Creates columns and sets buttons
col_buttons, col_graphs = strl.columns([1, 3])

with col_buttons:

    #Defines expander container
    expander_metrics_cfrisk = strl.expander(label='Metrics for confluence risk', expanded=True)
    with expander_metrics_cfrisk:

        #Creates metrics buttons to select
            #Technical
        strl.subheader("Technical")
        var_timechannel = strl.checkbox('Time channel', value = True)
        var_MAlograt = strl.checkbox('MA log rat', value = True)

            #Onchain
        strl.subheader("On-chain")
        var_nupl = strl.checkbox('NUPL', value = True)
        var_mvrvz = strl.checkbox('MVRV-Z', value = True)
        var_puellmultiple = strl.checkbox('Puell Multiple', value = True)
        var_thermocap = strl.checkbox('Thermocap rat.', value = True)
        var_supplyprofit = strl.checkbox('Supply in profit', value = True)

            #Sentiment
        strl.subheader("Sentiment")
        var_fg = strl.checkbox('Fear and Greed', value = True)
        var_fgMA = strl.checkbox('Fear and Greed MA', value = True)

#Defines metrics to create average
dict_var_bool = {"NUPL":var_nupl,
                'MVRV-Z':var_mvrvz,
                'Puell Multiple':var_puellmultiple,
                'Thermocap rat.':var_thermocap,
                'Supply in profit':var_supplyprofit,
                'Time channel':var_timechannel,
                'MA log rat':var_MAlograt,
                'Fear and Greed':var_fg,
                'Fear and Greed MA':var_fgMA
                }

#Creates a list of variables that are selected true
selected_cols_list = []
for metric in dict_var_bool:

    if dict_var_bool[metric] == True:
        selected_cols_list.extend([metric])

#Estimates average risk of selected columns
df_data['Confluence risk'] = df_data[selected_cols_list].mean(axis=1)

with col_graphs:

    #reports latest value
    last_cfrisk = df_data['Confluence risk'].iloc[-1]
    prev_val_cfrisk = df_data['Confluence risk'].iloc[-90]

    # strl.write("Latest value: " , round(last_cfrisk*100,2) , "%")

    fig_conf_bullet = bullet_fig_metric(value_in = last_cfrisk ,
                    previous_val = prev_val_cfrisk,
                    title_text = "Confluence risk",
                    ranges = [0, 0.25, 0.75, 1],
                    format_num = ",.1%",
                    log_scale = False
                    )
        
    strl.plotly_chart(fig_conf_bullet, use_container_width=True)

    #Defines expander container
    expander_cplots = strl.expander(label='Expand colored confluence risk history', expanded=True)
    with expander_cplots:

        #Plotly colored chart
        custom_cmap = [[0,"lawngreen"],[0.2,"greenyellow"], [0.4,"lemonchiffon"], [0.6,"sandybrown"], [0.8,"lightcoral"], [1,"crimson"]]
        access_warning()
        strl.plotly_chart(colored_metric(df_data, "Confluence risk", ".1%", color_map = custom_cmap, interactive = render), use_container_width=True, config = render_config)
        
    #Defines expander container
    expander_bplots = strl.expander(label='Expand bounded confluence risk history', expanded=False)
    with expander_bplots:

        # Plots confluence risk
        access_warning()
        strl.plotly_chart(bounded_metric(df_data,"Confluence risk", [0,0.25, 0.75, 1], metric_format = ".1%", log_scale = False, interactive =  render), use_container_width=True, config = render_config)

#Final comments
colored_header(label = "", description = "", color_name="yellow-80")
strl.write("Have you found this useful? Your donation will support our research and pave the way for innovative solutions.")

col1, col2, col3, col4 = strl.columns([1.5, 1.5, 5, 4])

with col1:
    badge(type="twitter", name="barbosa83")
with col2:
    badge(type="buymeacoffee", name="juandavid7E")
with col3:
    strl.caption("₿: 3EbH7JPSTGqSzyKKAijgva1ffXaY6JWk34")

button(username="juandavid7E",
       text = "Buy me a coffee",
       bg_color = '#FFDD00',
    #    emoji = "🍺",
       floating=False, width=220)




