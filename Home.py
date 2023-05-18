import pandas as pd
import numpy as np
import streamlit as strl

from datetime import date, timedelta
import datetime

from functions import bullet_fig_metric, market_data, aws_crypto_api

#Gets latest price data
btc_price, eth_price, btc_per, eth_per, btc_mcap, eth_mcap, crypto_mcap = market_data()

#Sets page configuration
strl.set_page_config(layout="wide", page_title="Home - BTC: " + str(btc_price), page_icon = "💰")

# Title
strl.image("bitcoin_strip.png", use_column_width = True)
strl.write("Have you found this useful? Consider donating - BTC: 3EbH7JPSTGqSzyKKAijgva1ffXaY6JWk34")
strl.caption("https://bmc.link/juandavid7E")

# Summary
strl.markdown("""---""")
strl.caption("Powered by CoinGecko and Python Analytics")
strl.header("Market summary")

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

strl.markdown("""---""")
strl.write("Have you found this useful? Consider donating - BTC: 3EbH7JPSTGqSzyKKAijgva1ffXaY6JWk34")
strl.caption("https://bmc.link/juandavid7E")
strl.caption("Unlock the potential of data science and bitcoin analysis to create a brighter financial future for all. Your donation will support our research and pave the way for innovative solutions. (BTC address: 3EbH7JPSTGqSzyKKAijgva1ffXaY6JWk34). Stay tunned, and keep accumulating!")

