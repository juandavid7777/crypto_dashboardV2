import pandas as pd
import numpy as np
import streamlit as strl

from functions import api_gn_bullet_data, api_tech_bullet_data, api_fg_bullet_data, bullet_fig_metric, market_data


#Gets latest price
btc_price, eth_price, btc_per, eth_per, btc_mcap, eth_mcap, crypto_mcap = market_data()

strl.set_page_config(layout="wide", page_title="HomeV2 - BTC: " + str(btc_price), page_icon = "💰")

#Imports the data - Should be secret
df_thresholds = pd.read_csv("thresholds.csv")

# Title
strl.image("bitcoin_strip.png", use_column_width = True)
# strl.markdown('<b style="color:darkgoldenrod ; font-size: 44px">BITCOIN metrics</b>', unsafe_allow_html=True)

# Summary
strl.markdown("""---""")
strl.caption("Powered by CoinGecko")
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
    # strl.write("")



#Adds metrics in columns
strl.markdown("""---""")
strl.caption("Powered by Coingecko, CryptoQuant, Glassnode and Alternative.me")
strl.header("Metrics")
col_tech, col_onchain, col_sent = strl.columns(3)

# Technical
with col_tech:
   strl.subheader("Technical")
   
   #Runs functions in loops
   df = df_thresholds[df_thresholds["type"].isin(["Technical"])]
   for i, metric in enumerate(df["metric_name"]):
        # Defines the source of data to be used
        if df.iloc[i]["type"] == "Onchain":
            val, prev_val, min_val, max_val = api_gn_bullet_data(metric, df.iloc[i]["api_id"])
        elif df.iloc[i]["type"] == "Technical":
            val, prev_val, min_val, max_val = api_tech_bullet_data(metric, df.iloc[i]["api_id"])
        else:
            val, prev_val, min_val, max_val = api_fg_bullet_data(metric, df.iloc[i]["api_id"])
        
        # Defines ranges to be used
        if df.iloc[i]["custom_limit"] == True:
            range_vals = [df.iloc[i]["min"], df.iloc[i]["low"], df.iloc[i]["high"], df.iloc[i]["max"]]
            
        else:
            range_vals = [min_val, df.iloc[i]["low"], df.iloc[i]["high"], max_val]

        # Plots data
        fig = bullet_fig_metric(value_in = val,
                    previous_val = prev_val,
                    title_text = metric,
                    ranges = range_vals,
                    format_num = df.iloc[i]["format"],
                    log_scale = df.iloc[i]["log_scale"]
                    )
        
        strl.plotly_chart(fig, use_container_width=True)


# Onchain
with col_onchain:
   strl.subheader("On-Chain")

   #Runs functions in loops
   df = df_thresholds[df_thresholds["type"].isin(["Onchain"])]
   for i, metric in enumerate(df["metric_name"]):
        # Defines the source of data to be used
        if df.iloc[i]["type"] == "Onchain":
            val, prev_val, min_val, max_val = api_gn_bullet_data(metric, df.iloc[i]["api_id"])
        elif df.iloc[i]["type"] == "Technical":
            val, prev_val, min_val, max_val = api_tech_bullet_data(metric, df.iloc[i]["api_id"])
        else:
            val, prev_val, min_val, max_val = api_fg_bullet_data(metric, df.iloc[i]["api_id"])
        
        # Defines ranges to be used
        if df.iloc[i]["custom_limit"] == True:
            range_vals = [df.iloc[i]["min"], df.iloc[i]["low"], df.iloc[i]["high"], df.iloc[i]["max"]]
            
        else:
            range_vals = [min_val, df.iloc[i]["low"], df.iloc[i]["high"], max_val]

        # Plots data
        fig = bullet_fig_metric(value_in = val,
                    previous_val = prev_val,
                    title_text = metric,
                    ranges = range_vals,
                    format_num = df.iloc[i]["format"],
                    log_scale = df.iloc[i]["log_scale"]
                    )
        
        strl.plotly_chart(fig, use_container_width=True)

# Sentiment
with col_sent:
   strl.subheader("Sentiment")

   #Runs functions in loops
   df = df_thresholds[df_thresholds["type"].isin(["Sentiment"])]
   for i, metric in enumerate(df["metric_name"]):
        # Defines the source of data to be used
        if df.iloc[i]["type"] == "Onchain":
            val, prev_val, min_val, max_val = api_gn_bullet_data(metric, df.iloc[i]["api_id"])
        elif df.iloc[i]["type"] == "Technical":
            val, prev_val, min_val, max_val = api_tech_bullet_data(metric, df.iloc[i]["api_id"])
        else:
            val, prev_val, min_val, max_val = api_fg_bullet_data(metric, df.iloc[i]["api_id"])
        
        # Defines ranges to be used
        if df.iloc[i]["custom_limit"] == True:
            range_vals = [df.iloc[i]["min"], df.iloc[i]["low"], df.iloc[i]["high"], df.iloc[i]["max"]]
            
        else:
            range_vals = [min_val, df.iloc[i]["low"], df.iloc[i]["high"], max_val]

        # Plots data
        fig = bullet_fig_metric(value_in = val,
                    previous_val = prev_val,
                    title_text = metric,
                    ranges = range_vals,
                    format_num = df.iloc[i]["format"],
                    log_scale = df.iloc[i]["log_scale"]
                    )
        
        strl.plotly_chart(fig, use_container_width=True)



strl.markdown("""---""")
strl.write("Have you found this useful? Consider donating - BTC: 3EbH7JPSTGqSzyKKAijgva1ffXaY6JWk34")
strl.caption("Unlock the potential of data science and bitcoin analysis to create a brighter financial future for all. Your donation will support our research and pave the way for innovative solutions. (BTC address: 3EbH7JPSTGqSzyKKAijgva1ffXaY6JWk34). Stay tunned, and keep accumulating!")
